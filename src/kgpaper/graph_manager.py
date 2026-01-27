import json
import uuid
from pathlib import Path
from rdflib import Graph, URIRef
from .config import load_config
from .ontology import KG, PREFIXES

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
                print(f"Error loading graph: {e}")
                # Fallback to empty graph or backup?
                
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

    def import_graph(self, file_path: str):
        """Imports an external RDF file."""
        try:
            # Auto-detect format based on extension or try common ones
            format = "turtle" if file_path.endswith(".ttl") else "json-ld" if file_path.endswith(".json") or file_path.endswith(".jsonld") else "xml"
            
            # 一時的なグラフにパースしてバリデーション
            temp_graph = Graph()
            temp_graph.parse(file_path, format=format)
            
            # paperTitleのバリデーション
            query = "SELECT ?title WHERE { ?s kg:paperTitle ?title }"
            for row in temp_graph.query(query, initNs=PREFIXES):
                self._validate_paper_title(str(row.title))
            
            # バリデーション成功後、本グラフに追加
            self.g.parse(file_path, format=format)
            self.save_graph()
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
        
        results = self.g.query(query, initBindings={'target_paper': paper_ref})
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
        self.save_graph() # Overwrite with empty

    def get_all_papers(self):
        """Returns list of paper metadata for management UI."""
        query = """
        SELECT ?paper ?title ?type ?source
        WHERE {
            ?paper a kg:Paper ;
                   kg:paperTitle ?title ;
                   kg:documentType ?type .
            OPTIONAL { ?paper kg:sourceFile ?source }
        }
        """
        results = self.g.query(query)
        return [{"uri": str(row.paper), "title": str(row.title), "type": str(row.type), "source": str(row.source) if row.source else ""} for row in results]

