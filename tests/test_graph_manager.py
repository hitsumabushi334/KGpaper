import pytest
import os
from pathlib import Path
from kgpaper.graph_manager import GraphManager
from kgpaper.ontology import KG, PREFIXES

@pytest.fixture
def graph_manager(tmp_path):
    # Mock config to use tmp_path
    config_path = tmp_path / "config.yaml"
    graph_dir = tmp_path / "graphs"
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(f"""
storage:
  graph_dir: "{str(graph_dir).replace(os.sep, '/')}"
""")
    
    return GraphManager(config_path=str(config_path))

def test_add_json_ld(graph_manager):
    data = {
        "@context": {
            "kg": "http://example.org/kgpaper/",
            "Paper": "kg:Paper",
            "paperTitle": "kg:paperTitle"
        },
        "@id": "urn:uuid:123",
        "@type": "kg:Paper",
        "paperTitle": "Test Paper"
    }
    
    graph_manager.add_json_ld(data)
    
    # Verify graph contains the triple
    q = """
    SELECT ?title
    WHERE {
        ?s a kg:Paper ;
           kg:paperTitle ?title .
    }
    """
    results = list(graph_manager.g.query(q))
    assert len(results) == 1
    assert str(results[0].title) == "Test Paper"

def test_delete_paper(graph_manager):
    # Add data
    data = {
        "@context": {
            "kg": "http://example.org/kgpaper/",
            "Paper": "kg:Paper",
            "paperTitle": "kg:paperTitle"
        },
        "@id": "urn:uuid:123",
        "@type": "kg:Paper",
        "paperTitle": "Test Paper"
    }
    graph_manager.add_json_ld(data)
    
    # Delete
    graph_manager.delete_paper("urn:uuid:123")
    
    # Verify empty
    q = "SELECT ?title WHERE { ?s dl:paperTitle ?title }"
    assert len(list(graph_manager.g.query(q))) == 0
    
    # Verify triples are gone
    assert len(graph_manager.g) == 0

def test_clear_all(graph_manager):
     data = {
        "@context": {"kg": "http://example.org/kgpaper/"},
        "@id": "urn:uuid:123",
        "@type": "kg:Paper"
    }
     graph_manager.add_json_ld(data)
     assert len(graph_manager.g) > 0
     
     graph_manager.clear_all()
     assert len(graph_manager.g) == 0 # Or close to 0 (prefixes might remain? namespace binding doesn't add triples)
