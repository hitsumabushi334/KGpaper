from rdflib import Graph
from .ontology import KG, PREFIXES


class SparqlQuery:
    def __init__(self, graph: Graph):
        self.g = graph

    def _escape_sparql_string(self, value: str) -> str:
        """SPARQL文字列リテラル用にエスケープする"""
        # バックスラッシュを先にエスケープ、次にダブルクォート
        return value.replace("\\", "\\\\").replace('"', '\\"')

    def search(
        self,
        paper_title: str | None = None,
        source_context: str | None = None,
        experiment_type: str | None = None,
        content_type: str | None = None,
    ):
        """
        Executes a SPARQL query with optional filters.
        Returns a list of dicts with result data.
        """

        # Base query structure to retrieve nodes for visualization
        # We want triples that form the path: Paper -> Experiment -> Content
        # But for visualization, we might just want the list of matching contents
        # or triples to build a subgraph.

        # Let's return a table of data suitable for filtering,
        # and also include URIs to build the graph later.

        filters = []
        if paper_title:
            escaped_title = self._escape_sparql_string(paper_title)
            filters.append(f'FILTER(CONTAINS(LCASE(?title), LCASE("{escaped_title}")))')
        if source_context and source_context != "All":
            escaped_src = self._escape_sparql_string(source_context)
            filters.append(f'FILTER(CONTAINS(?srcCtx, "{escaped_src}"))')
        if experiment_type and experiment_type != "All":
            # UIからはkg:Synthesis形式で来る。
            # データがURIの場合（例: <.../Synthesis>）と、Literalの場合（例: "kg:Synthesis"）の両方に対応
            filters.append(
                f'FILTER(?expType = {experiment_type} || STR(?expType) = "{experiment_type}")'
            )
        if content_type and content_type != "All":
            escaped_cont = self._escape_sparql_string(content_type)
            filters.append(f'FILTER(?contType = "{escaped_cont}")')

        filter_str = "\n".join(filters)

        query = f"""
        SELECT ?paper ?title ?exp ?expType ?cont ?contType ?srcCtx ?text
        WHERE {{
            ?paper a kg:Paper ;
                   kg:paperTitle ?title .
            
            ?paper kg:hasExperiment ?exp .
            ?exp kg:experimentType ?expType .
            
            ?exp kg:hasContent ?cont .
            ?cont kg:contentType ?contType ;
                  kg:text ?text .
            OPTIONAL {{ ?cont kg:sourceContext ?srcCtx }}
                  
            {filter_str}
        }}
        """

        results = self.g.query(query, initNs=PREFIXES)

        # 集約用辞書: content_uri -> data dict
        aggregated_data = {}

        for row in results:
            content_uri = str(row.cont)
            src_ctx = str(row.srcCtx) if row.srcCtx else ""

            if content_uri not in aggregated_data:
                aggregated_data[content_uri] = {
                    "paper_uri": str(row.paper),
                    "paper_title": str(row.title),
                    "experiment_uri": str(row.exp),
                    "experiment_type": str(row.expType).split("/")[-1],
                    "content_uri": content_uri,
                    "content_type": str(row.contType),
                    "source_contexts": set(),  # Setで重複排除して集める
                    "text": str(row.text),
                }

            if src_ctx:
                aggregated_data[content_uri]["source_contexts"].add(src_ctx)

        # リスト形式に変換して返す
        data = []
        for item in aggregated_data.values():
            # source_contextsをカンマ区切り文字列に変換
            src_ctxs = sorted(list(item["source_contexts"]))
            item["source_context"] = ", ".join(src_ctxs)
            del item["source_contexts"]  # 中間データを削除
            data.append(item)

        return data

    def export_all_triples(self):
        """Returns all triples for bulk export or visualization without filters."""
        # Or maybe utilize filter to construct sub-graph
        pass
