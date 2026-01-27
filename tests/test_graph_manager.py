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
    q = "SELECT ?title WHERE { ?s kg:paperTitle ?title }"
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


def test_load_graph_with_existing_file(tmp_path):
    """既存のグラフファイルを読み込むテスト"""
    config_path = tmp_path / "config.yaml"
    graph_dir = tmp_path / "graphs"
    graph_dir.mkdir()
    
    # 有効なTurtleファイルを作成
    graph_file = graph_dir / "knowledge_graph.ttl"
    graph_file.write_text("""
@prefix kg: <http://example.org/kgpaper/> .

<urn:uuid:existing> a kg:Paper ;
    kg:paperTitle "Existing Paper" .
""", encoding="utf-8")
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(f"""
storage:
  graph_dir: "{str(graph_dir).replace(os.sep, '/')}"
""")
    
    gm = GraphManager(config_path=str(config_path))
    
    # 既存のトリプルがロードされていることを確認
    assert len(gm.g) > 0


def test_load_graph_with_invalid_file(tmp_path, capsys):
    """不正なグラフファイルを読み込んだ際のエラーハンドリングテスト"""
    config_path = tmp_path / "config.yaml"
    graph_dir = tmp_path / "graphs"
    graph_dir.mkdir()
    
    # 不正なTurtleファイルを作成
    graph_file = graph_dir / "knowledge_graph.ttl"
    graph_file.write_text("This is not valid turtle syntax @@@###", encoding="utf-8")
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(f"""
storage:
  graph_dir: "{str(graph_dir).replace(os.sep, '/')}"
""")
    
    # エラーが発生してもクラッシュせずにインスタンスが作成される
    gm = GraphManager(config_path=str(config_path))
    
    # エラーメッセージが出力されていることを確認
    captured = capsys.readouterr()
    assert "Error loading graph" in captured.out


def test_import_graph_turtle(graph_manager, tmp_path):
    """Turtle形式のRDFファイルをインポートするテスト"""
    rdf_file = tmp_path / "import.ttl"
    rdf_file.write_text("""
@prefix kg: <http://example.org/kgpaper/> .

<urn:uuid:imported> a kg:Paper ;
    kg:paperTitle "Imported Paper" .
""", encoding="utf-8")
    
    graph_manager.import_graph(str(rdf_file))
    
    # インポートされたトリプルがあることを確認
    q = "SELECT ?title WHERE { ?s kg:paperTitle ?title }"
    results = list(graph_manager.g.query(q))
    assert len(results) == 1
    assert str(results[0].title) == "Imported Paper"


def test_import_graph_json_ld(graph_manager, tmp_path):
    """JSON-LD形式のRDFファイルをインポートするテスト"""
    rdf_file = tmp_path / "import.json"
    rdf_file.write_text("""{
  "@context": {"kg": "http://example.org/kgpaper/"},
  "@id": "urn:uuid:json-imported",
  "@type": "kg:Paper",
  "kg:paperTitle": "JSON Imported Paper"
}""", encoding="utf-8")
    
    graph_manager.import_graph(str(rdf_file))
    
    assert len(graph_manager.g) > 0


def test_import_graph_jsonld_extension(graph_manager, tmp_path):
    """拡張子 .jsonld のRDFファイルをインポートするテスト"""
    rdf_file = tmp_path / "import.jsonld"
    rdf_file.write_text("""{
  "@context": {"kg": "http://example.org/kgpaper/"},
  "@id": "urn:uuid:jsonld-imported",
  "@type": "kg:Paper"
}""", encoding="utf-8")
    
    graph_manager.import_graph(str(rdf_file))
    
    assert len(graph_manager.g) > 0


def test_import_graph_xml(graph_manager, tmp_path):
    """RDF/XML形式のファイル(その他の拡張子)をインポートするテスト"""
    rdf_file = tmp_path / "import.rdf"
    rdf_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:kg="http://example.org/kgpaper/">
  <rdf:Description rdf:about="urn:uuid:xml-imported">
    <rdf:type rdf:resource="http://example.org/kgpaper/Paper"/>
    <kg:paperTitle>XML Imported Paper</kg:paperTitle>
  </rdf:Description>
</rdf:RDF>""", encoding="utf-8")
    
    graph_manager.import_graph(str(rdf_file))
    
    assert len(graph_manager.g) > 0


def test_import_graph_error(graph_manager, tmp_path):
    """不正なRDFファイルをインポートした際のValueErrorテスト"""
    rdf_file = tmp_path / "invalid.ttl"
    rdf_file.write_text("This is not valid RDF @@@", encoding="utf-8")
    
    with pytest.raises(ValueError) as exc_info:
        graph_manager.import_graph(str(rdf_file))
    
    assert "Failed to import graph" in str(exc_info.value)


def test_get_all_papers(graph_manager):
    """論文一覧を取得するテスト"""
    data = {
        "@context": {
            "kg": "http://example.org/kgpaper/",
            "Paper": "kg:Paper",
            "paperTitle": "kg:paperTitle",
            "documentType": "kg:documentType",
            "sourceFile": "kg:sourceFile"
        },
        "@id": "urn:uuid:paper1",
        "@type": "kg:Paper",
        "paperTitle": "Test Paper 1",
        "documentType": "main",
        "sourceFile": "test.pdf"
    }
    graph_manager.add_json_ld(data)
    
    papers = graph_manager.get_all_papers()
    
    assert len(papers) == 1
    assert papers[0]["title"] == "Test Paper 1"
    assert papers[0]["type"] == "main"
    assert papers[0]["source"] == "test.pdf"
    assert papers[0]["uri"] == "urn:uuid:paper1"


def test_get_all_papers_empty(graph_manager):
    """論文がない場合の空リスト取得テスト"""
    papers = graph_manager.get_all_papers()
    
    assert papers == []


def test_get_all_papers_without_source(graph_manager):
    """sourceFile がない論文の取得テスト"""
    data = {
        "@context": {
            "kg": "http://example.org/kgpaper/",
            "Paper": "kg:Paper",
            "paperTitle": "kg:paperTitle",
            "documentType": "kg:documentType"
        },
        "@id": "urn:uuid:paper-no-source",
        "@type": "kg:Paper",
        "paperTitle": "Paper Without Source",
        "documentType": "support"
    }
    graph_manager.add_json_ld(data)
    
    papers = graph_manager.get_all_papers()
    
    assert len(papers) == 1
    assert papers[0]["source"] == ""  # OPTIONAL なので空文字列


def test_delete_paper_preserves_other_papers(graph_manager):
    """論文削除が他の論文に影響を与えないことを確認するテスト"""
    # 2つの論文を追加
    paper1 = {
        "@context": {
            "kg": "http://example.org/kgpaper/",
            "Paper": "kg:Paper",
            "paperTitle": "kg:paperTitle"
        },
        "@id": "urn:uuid:paper-1",
        "@type": "kg:Paper",
        "paperTitle": "Paper One"
    }
    paper2 = {
        "@context": {
            "kg": "http://example.org/kgpaper/",
            "Paper": "kg:Paper",
            "paperTitle": "kg:paperTitle"
        },
        "@id": "urn:uuid:paper-2",
        "@type": "kg:Paper",
        "paperTitle": "Paper Two"
    }
    graph_manager.add_json_ld(paper1)
    graph_manager.add_json_ld(paper2)
    
    # paper1のみ削除
    graph_manager.delete_paper("urn:uuid:paper-1")
    
    # paper2は残っていることを確認
    q = "SELECT ?title WHERE { ?s kg:paperTitle ?title }"
    results = list(graph_manager.g.query(q))
    assert len(results) == 1
    assert str(results[0].title) == "Paper Two"


def test_validate_empty_paper_title(graph_manager):
    """空のpaperTitleをバリデーションで拒否するテスト"""
    data = {
        "@context": {
            "kg": "http://example.org/kgpaper/",
            "Paper": "kg:Paper",
            "paperTitle": "kg:paperTitle"
        },
        "@id": "urn:uuid:empty-title",
        "@type": "kg:Paper",
        "paperTitle": ""  # 空文字列
    }
    
    with pytest.raises(ValueError) as exc_info:
        graph_manager.add_json_ld(data)
    
    assert "Paper title cannot be empty" in str(exc_info.value)


def test_validate_whitespace_only_paper_title(graph_manager):
    """空白のみのpaperTitleをバリデーションで拒否するテスト"""
    data = {
        "@context": {
            "kg": "http://example.org/kgpaper/",
            "Paper": "kg:Paper",
            "paperTitle": "kg:paperTitle"
        },
        "@id": "urn:uuid:whitespace-title",
        "@type": "kg:Paper",
        "paperTitle": "   "  # 空白のみ
    }
    
    with pytest.raises(ValueError) as exc_info:
        graph_manager.add_json_ld(data)
    
    assert "Paper title cannot be empty" in str(exc_info.value)
