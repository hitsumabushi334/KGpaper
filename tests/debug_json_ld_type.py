import pytest
from rdflib import Graph, URIRef, Literal
from kgpaper.graph_manager import GraphManager
from kgpaper.ontology import KG, PREFIXES


def test_json_ld_experiment_type_parsing(tmp_path):
    # Create a minimal JSON-LD file with experimentType
    json_ld = {
        "@context": {
            "kg": "http://example.org/kgpaper/",
            "experimentType": "kg:experimentType",
            "Experiment": "kg:Experiment",
        },
        "@id": "urn:uuid:p1",
        "@type": "kg:Paper",
        "kg:hasExperiment": {
            "@id": "urn:uuid:e1",
            "@type": "kg:Experiment",
            "experimentType": "kg:Synthesis",
        },
    }

    gm = GraphManager(config_path="config.yaml")  # config_path is dummy but needed
    # We can just use gm.add_json_ld logic or raw graph parse

    # Use raw graph parse to simulate loading
    import json

    g = Graph()
    g.parse(data=json.dumps(json_ld), format="json-ld")

    # Check the object of experimentType
    query = """
    SELECT ?type
    WHERE {
        ?s kg:experimentType ?type .
    }
    """

    results = list(g.query(query, initNs=PREFIXES))
    assert len(results) > 0
    obj = results[0].type

    print(f"\nType of object: {type(obj)}")
    print(f"Value of object: {obj}")

    # Check if it is URIRef or Literal
    if isinstance(obj, URIRef):
        print(" It is a URIRef")
    elif isinstance(obj, Literal):
        print(" It is a Literal")

    # Also test SPARQL filter match
    # Scenario 1: treat as URI
    # Scenario 2: treat as Literal "kg:Synthesis"

    filter_uri_query = """
    SELECT ?s WHERE {
        ?s kg:experimentType ?type .
        FILTER(?type = kg:Synthesis)
    }
    """
    assert (
        len(list(g.query(filter_uri_query, initNs=PREFIXES))) == 1
    ), "Failed to match as URI"
