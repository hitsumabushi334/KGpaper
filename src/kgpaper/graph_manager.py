import logging
import json
import uuid
from pathlib import Path
from rdflib import Graph, URIRef
from .config import load_config
from .ontology import KG, PREFIXES

logger = logging.getLogger(__name__)


class GraphManager:
    def __init__(self, config_path="config.yaml"):
        self.config = load_config(config_path)
        self.graph_dir = self.config.graph_dir
        self.graph_dir.mkdir(parents=True, exist_ok=True)
        self.graph_file = self.graph_dir / "knowledge_graph.ttl"
        self.g = Graph()
        self._bind_prefixes()
        self.load_graph()

    def _bind_prefixes(self):
        for prefix, namespace in PREFIXES.items():
            self.g.bind(prefix, namespace)

    def load_graph(self):
        if self.graph_file.exists():
            try:
                self.g.parse(self.graph_file, format="turtle")
            except Exception as e:
                logger.error(f"グラフ読み込み失敗: {e}", exc_info=True)
                raise  # UI側でハンドリング可能にする

    def save_graph(self):
        self.g.serialize(destination=self.graph_file, format="turtle")

    def _escape_sparql_string(self, value: str) -> str:
        """SPARQL文字列リテラル用にエスケープする"""
        return value.replace("\\", "\\\\").replace('"', '\\"')

    def _validate_paper_title(self, title: str) -> str:
        """論文タイトルのバリデーション"""
        if not title or not title.strip():
            raise ValueError("Paper title cannot be empty")
        return title.strip()

    # 各エンティティの必須プロパティ
    REQUIRED_PROPERTIES = {
        "kg:Paper": ["kg:paperTitle", "kg:documentType"],
        "kg:Experiment": ["kg:experimentType"],
        "kg:Method": ["kg:contentType", "kg:text"],
        "kg:Result": ["kg:contentType", "kg:text"],
        "kg:Discussion": ["kg:contentType", "kg:text"],
        "kg:Conclusion": ["kg:contentType", "kg:text"],
    }

    def _validate_required_properties(self, graph: Graph):
        """全エンティティの必須プロパティをチェック"""
        for entity_type, props in self.REQUIRED_PROPERTIES.items():
            for prop in props:
                query = f"""
                    SELECT ?entity WHERE {{
                        ?entity a {entity_type} .
                        FILTER NOT EXISTS {{ ?entity {prop} ?val }}
                    }}
                """
                missing = list(graph.query(query, initNs=PREFIXES))
                if missing:
                    raise ValueError(f"{entity_type} must have {prop}")

    def add_json_ld(self, json_data: dict):
        """Adds JSON-LD data to the graph."""
        # Check if @context is present, if not, might need to inject or assume
        # The prompt output should have @context.

        # バリデーション: paperTitleが存在する場合はチェック
        if "kg:paperTitle" in json_data:
            self._validate_paper_title(json_data["kg:paperTitle"])
        elif "paperTitle" in json_data:
            self._validate_paper_title(json_data["paperTitle"])

        # rdflib's parse can handle json-ld string
        json_str = json.dumps(json_data)
        self.g.parse(data=json_str, format="json-ld")
        self.save_graph()

    @staticmethod
    def validate_json_ld_structure(json_data: dict) -> None:
        """JSON-LDの構造（@context, @type）を検証する。問題があればValueErrorを送出。"""
        if not isinstance(json_data, dict):
            raise ValueError("JSON-LD must be a dictionary")
        if "@context" not in json_data:
            raise ValueError("Missing @context in JSON-LD")
        if "@type" not in json_data:
            raise ValueError("Missing @type in JSON-LD")

    def import_graph(self, file_path: str):
        """Imports an external RDF file."""
        # 拡張子チェックからxmlを削除
        if file_path.endswith(".xml"):
            raise ValueError("XML format is not supported")

        format = "turtle" if file_path.endswith(".ttl") else "json-ld"

        # JSON系の場合は構造バリデーション
        if format == "json-ld":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.validate_json_ld_structure(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON file: {e}")

        try:
            # 一時的なグラフにパースしてバリデーション
            temp_graph = Graph()
            temp_graph.parse(file_path, format=format)

            # paperTitleのバリデーション
            query = "SELECT ?title WHERE { ?s kg:paperTitle ?title }"
            for row in temp_graph.query(query, initNs=PREFIXES):
                self._validate_paper_title(str(row.title))

            # 必須プロパティのバリデーション
            self._validate_required_properties(temp_graph)

            # バリデーション成功後、本グラフに追加
            self.g.parse(file_path, format=format)
            self.save_graph()
        except ValueError:
            raise  # バリデーションエラーはそのまま再送出
        except Exception as e:
            raise ValueError(f"Failed to import graph: {e}")

    def delete_paper(self, paper_uri: str):
        """
        Deletes a paper and its associated experiments/contents.
        This requires a SPARQL DELETE WHERE/Update or selective removal.
        Since rdflib Memory store doesn't support SPARQL Update efficiently always,
        we can iterate and remove.
        """
        # Strategy: Find all sub-nodes (Experiment, Content) linked to this Paper
        # and remove them.

        paper_ref = URIRef(paper_uri)

        # 1. Provide a query to find all related triples
        # Pattern:
        # ?paper ?p ?o .
        # ?paper kg:hasExperiment ?exp . ?exp ?p2 ?o2 .
        # ?exp kg:hasContent ?cont . ?cont ?p3 ?o3 .

        # We can use SPARQL to select distinct subjects to delete
        query = """
        SELECT DISTINCT ?s
        WHERE {
            BIND(?target_paper AS ?paper)
            {
                ?paper ?p ?o .
                BIND(?paper AS ?s)
            }
            UNION
            {
                ?paper kg:hasExperiment ?exp .
                ?exp ?p2 ?o2 .
                BIND(?exp AS ?s)
            }
            UNION
            {
                ?paper kg:hasExperiment ?exp .
                ?exp kg:hasContent ?cont .
                ?cont ?p3 ?o3 .
                BIND(?cont AS ?s)
            }
        }
        """

        results = self.g.query(query, initBindings={"target_paper": paper_ref})
        subjects_to_remove = [row.s for row in results]

        for s in subjects_to_remove:
            self.g.remove((s, None, None))

        # Also remove incoming links to the paper? (e.g. lists)
        self.g.remove((None, None, paper_ref))

        self.save_graph()

    def clear_all(self):
        """Clears the entire graph."""
        self.g = Graph()
        self._bind_prefixes()
        self.save_graph()  # Overwrite with empty

    def get_all_papers(self):
        """Returns list of paper metadata for management UI."""
        query = """
        SELECT ?paper ?title ?type ?source
        WHERE {
            ?paper a kg:Paper ;
                   kg:paperTitle ?title .
            OPTIONAL { ?paper kg:documentType ?type }
            OPTIONAL { ?paper kg:sourceFile ?source }
        }
        """
        results = self.g.query(query)
        return [
            {
                "uri": str(row.paper),
                "title": str(row.title),
                "type": str(row.type) if row.type else "",
                "source": str(row.source) if row.source else "",
            }
            for row in results
        ]
