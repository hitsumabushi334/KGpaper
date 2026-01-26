from rdflib import Graph
from .ontology import KG, PREFIXES

class SparqlQuery:
    def __init__(self, graph: Graph):
        self.g = graph

    def search(self, 
               paper_title: str = None, 
               document_type: str = None, 
               experiment_type: str = None, 
               content_type: str = None):
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
             filters.append(f'FILTER(CONTAINS(LCASE(?title), LCASE("{paper_title}")))')
        if document_type:
             filters.append(f'FILTER(?docType = "{document_type}")')
        if experiment_type and experiment_type != "All":
             filters.append(f'FILTER(?expType = kg:{experiment_type})') # Assuming enum URI matches
        if content_type and content_type != "All":
             filters.append(f'FILTER(?contType = "{content_type}")') # Assuming literal or URI? In prompt/ontology it's literal string for contentType

        filter_str = "\n".join(filters)
        
        query = f"""
        SELECT ?paper ?title ?docType ?exp ?expType ?cont ?contType ?text
        WHERE {{
            ?paper a kg:Paper ;
                   kg:paperTitle ?title ;
                   kg:documentType ?docType .
            
            ?paper kg:hasExperiment ?exp .
            ?exp kg:experimentType ?expType .
            
            ?exp kg:hasContent ?cont .
            ?cont kg:contentType ?contType ;
                  kg:text ?text .
                  
            {filter_str}
        }}
        """
        
        results = self.g.query(query)
        
        data = []
        for row in results:
            data.append({
                "paper_uri": str(row.paper),
                "paper_title": str(row.title),
                "document_type": str(row.docType),
                "experiment_uri": str(row.exp),
                "experiment_type": str(row.expType).split("/")[-1], # Simplify
                "content_uri": str(row.cont),
                "content_type": str(row.contType),
                "text": str(row.text)
            })
            
        return data

    def export_all_triples(self):
         """Returns all triples for bulk export or visualization without filters."""
         # Or maybe utilize filter to construct sub-graph
         pass
