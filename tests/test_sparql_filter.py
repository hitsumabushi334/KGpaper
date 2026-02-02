import pytest
from rdflib import Graph, URIRef, Literal
from kgpaper.sparql_query import SparqlQuery
from kgpaper.ontology import KG


def test_search_filter_by_experiment_type():
    g = Graph()

    # Define URIs
    paper_uri = URIRef("urn:uuid:paper1")

    # Experiment 1: Synthesis
    exp_syn = URIRef("urn:uuid:exp_syn")
    g.add((paper_uri, KG.hasExperiment, exp_syn))
    g.add((exp_syn, KG.experimentType, KG.Synthesis))
    g.add((exp_syn, KG.hasContent, URIRef("urn:uuid:c1")))
    g.add((URIRef("urn:uuid:c1"), KG.contentType, Literal("method")))
    g.add((URIRef("urn:uuid:c1"), KG.text, Literal("Syn method")))

    # Experiment 2: Characterization
    exp_char = URIRef("urn:uuid:exp_char")
    g.add((paper_uri, KG.hasExperiment, exp_char))
    g.add((exp_char, KG.experimentType, KG.Characterization))
    g.add((exp_char, KG.hasContent, URIRef("urn:uuid:c2")))
    g.add((URIRef("urn:uuid:c2"), KG.contentType, Literal("method")))
    g.add((URIRef("urn:uuid:c2"), KG.text, Literal("Char method")))

    # Setup Paper triples as well (required for query)
    g.add(
        (paper_uri, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), KG.Paper)
    )
    g.add((paper_uri, KG.paperTitle, Literal("Test Paper")))

    sq = SparqlQuery(g)

    # Search for Synthesis only
    results = sq.search(experiment_type="kg:Synthesis")

    # Should only find 1 result (Synthesis)
    assert len(results) == 1
    assert results[0]["experiment_type"] == "Synthesis"

    # Test Case 2: Experiment Type as Literal "kg:Synthesis"
    # This simulates how data might be loaded from JSON-LD without explicit type mapping
    exp_lit = URIRef("urn:uuid:exp_lit")
    g.add((paper_uri, KG.hasExperiment, exp_lit))
    # Note: Adding as Literal string "kg:Synthesis"
    g.add((exp_lit, KG.experimentType, Literal("kg:Synthesis")))
    g.add((exp_lit, KG.hasContent, URIRef("urn:uuid:c3")))
    g.add((URIRef("urn:uuid:c3"), KG.contentType, Literal("result")))
    g.add((URIRef("urn:uuid:c3"), KG.text, Literal("Literal Type Result")))

    # Search again for Synthesis
    # Should now find 2 results (1 URI, 1 Literal)
    results_mixed = sq.search(experiment_type="kg:Synthesis")
    assert len(results_mixed) == 2
