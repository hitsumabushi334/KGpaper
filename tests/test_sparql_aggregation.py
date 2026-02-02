import pytest
from rdflib import Graph, URIRef, Literal
from kgpaper.sparql_query import SparqlQuery
from kgpaper.ontology import KG


def test_search_aggregation_multiple_source_contexts():
    # Setup graph with one content having multiple sourceContexts
    g = Graph()

    # Define URIs
    paper_uri = URIRef("urn:uuid:paper1")
    exp_uri = URIRef("urn:uuid:exp1")
    cont_uri = URIRef("urn:uuid:cont1")

    # Add triples
    # Paper
    g.add(
        (paper_uri, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), KG.Paper)
    )
    g.add((paper_uri, KG.paperTitle, Literal("Test Paper")))

    # Experiment
    g.add((paper_uri, KG.hasExperiment, exp_uri))
    g.add((exp_uri, KG.experimentType, KG.Synthesis))

    # Content
    g.add((exp_uri, KG.hasContent, cont_uri))
    g.add((cont_uri, KG.contentType, Literal("method")))
    g.add((cont_uri, KG.text, Literal("Some content text")))

    # Multiple sourceContexts (This causes duplication in raw SPARQL)
    g.add((cont_uri, KG.sourceContext, Literal("Main")))
    g.add((cont_uri, KG.sourceContext, Literal("Support")))

    sq = SparqlQuery(g)
    results = sq.search()

    # Before fix: Should have 2 results (one for Main, one for Support)
    # After fix: Should have 1 result with aggregated source_context

    # We expect the fix to make this assertion pass (len == 1)
    # But for TDD, we first confirm if it fails or how it behaves currently.

    assert len(results) == 1
    assert "Main" in results[0]["source_context"]
    assert "Support" in results[0]["source_context"]
