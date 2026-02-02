"""
sparql_query.py のテスト

SparqlQuery クラスの SPARQL 検索機能のテストを実施する。
"""
import pytest
from rdflib import Graph
from kgpaper.sparql_query import SparqlQuery
from kgpaper.ontology import PREFIXES


@pytest.fixture
def graph_with_data():
    """テスト用のRDFグラフを作成するフィクスチャ"""
    g = Graph()
    for prefix, namespace in PREFIXES.items():
        g.bind(prefix, namespace)
    
    # テストデータをTurtle形式で追加
    test_data = """
    @prefix kg: <http://example.org/kgpaper/> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

    <urn:uuid:paper1> a kg:Paper ;
        kg:paperTitle "Synthesis of Carbon Nanotubes" ;
        kg:documentType "main" ;
        kg:hasExperiment <urn:uuid:exp1> .

    <urn:uuid:exp1> a kg:Experiment ;
        kg:experimentType kg:Synthesis ;
        kg:hasContent <urn:uuid:content1> .

    <urn:uuid:content1> a kg:Content ;
        kg:contentType "Method" ;
        kg:text "CVD synthesis method was used..." .

    <urn:uuid:paper2> a kg:Paper ;
        kg:paperTitle "Electrochemical Analysis" ;
        kg:documentType "support" ;
        kg:hasExperiment <urn:uuid:exp2> .

    <urn:uuid:exp2> a kg:Experiment ;
        kg:experimentType kg:Electrochemical ;
        kg:hasContent <urn:uuid:content2> .

    <urn:uuid:content2> a kg:Content ;
        kg:contentType "Result" ;
        kg:text "Cyclic voltammetry showed..." .
    """
    g.parse(data=test_data, format="turtle")
    return g


@pytest.fixture
def empty_graph():
    """空のRDFグラフを作成するフィクスチャ"""
    g = Graph()
    for prefix, namespace in PREFIXES.items():
        g.bind(prefix, namespace)
    return g


class TestSparqlQueryInit:
    """SparqlQuery.__init__ のテスト"""

    def test_init_with_graph(self, graph_with_data):
        """グラフを渡してインスタンス化するテスト"""
        sq = SparqlQuery(graph_with_data)
        
        assert sq.g is graph_with_data


class TestSparqlQuerySearch:
    """SparqlQuery.search のテスト"""

    def test_search_no_filter(self, graph_with_data):
        """フィルタなしで全件検索するテスト"""
        sq = SparqlQuery(graph_with_data)
        
        results = sq.search()
        
        assert len(results) == 2
        # 結果に必要なフィールドが含まれていることを確認
        assert all("paper_uri" in r for r in results)
        assert all("paper_title" in r for r in results)
        assert all("document_type" in r for r in results)
        assert all("experiment_uri" in r for r in results)
        assert all("experiment_type" in r for r in results)
        assert all("content_uri" in r for r in results)
        assert all("content_type" in r for r in results)
        assert all("text" in r for r in results)

    def test_search_by_paper_title(self, graph_with_data):
        """タイトルでフィルタ検索するテスト"""
        sq = SparqlQuery(graph_with_data)
        
        results = sq.search(paper_title="Carbon")
        
        assert len(results) == 1
        assert "Carbon Nanotubes" in results[0]["paper_title"]

    def test_search_by_paper_title_case_insensitive(self, graph_with_data):
        """タイトル検索が大文字小文字を区別しないテスト"""
        sq = SparqlQuery(graph_with_data)
        
        results = sq.search(paper_title="carbon")
        
        assert len(results) == 1
        assert "Carbon Nanotubes" in results[0]["paper_title"]

    def test_search_by_document_type(self, graph_with_data):
        """ドキュメントタイプでフィルタ検索するテスト"""
        sq = SparqlQuery(graph_with_data)
        
        results = sq.search(document_type="main")
        
        assert len(results) == 1
        assert results[0]["document_type"] == "main"

    def test_search_by_experiment_type(self, graph_with_data):
        """実験タイプでフィルタ検索するテスト"""
        sq = SparqlQuery(graph_with_data)
        
        results = sq.search(experiment_type="kg:Synthesis")
        
        assert len(results) == 1
        assert "Synthesis" in results[0]["experiment_type"]

    def test_search_by_experiment_type_all(self, graph_with_data):
        """実験タイプ "All" の場合はフィルタをスキップするテスト"""
        sq = SparqlQuery(graph_with_data)
        
        results = sq.search(experiment_type="All")
        
        # "All" は全件を返すべき
        assert len(results) == 2

    def test_search_by_content_type(self, graph_with_data):
        """コンテンツタイプでフィルタ検索するテスト"""
        sq = SparqlQuery(graph_with_data)
        
        results = sq.search(content_type="Method")
        
        assert len(results) == 1
        assert results[0]["content_type"] == "Method"

    def test_search_by_content_type_all(self, graph_with_data):
        """コンテンツタイプ "All" の場合はフィルタをスキップするテスト"""
        sq = SparqlQuery(graph_with_data)
        
        results = sq.search(content_type="All")
        
        # "All" は全件を返すべき
        assert len(results) == 2

    def test_search_combined_filters(self, graph_with_data):
        """複数フィルタを組み合わせて検索するテスト"""
        sq = SparqlQuery(graph_with_data)
        
        results = sq.search(
            paper_title="Electrochemical",
            document_type="support",
            content_type="Result"
        )
        
        assert len(results) == 1
        assert results[0]["paper_title"] == "Electrochemical Analysis"

    def test_search_no_results(self, graph_with_data):
        """マッチする結果がない場合のテスト"""
        sq = SparqlQuery(graph_with_data)
        
        results = sq.search(paper_title="NonExistent")
        
        assert len(results) == 0

    def test_search_empty_graph(self, empty_graph):
        """空のグラフで検索するテスト"""
        sq = SparqlQuery(empty_graph)
        
        results = sq.search()
        
        assert len(results) == 0


class TestSparqlQueryExportAllTriples:
    """SparqlQuery.export_all_triples のテスト"""

    def test_export_all_triples(self, graph_with_data):
        """全トリプルエクスポートのテスト(現在は pass 実装)"""
        sq = SparqlQuery(graph_with_data)
        
        # 現在の実装は pass なので None を返す
        result = sq.export_all_triples()
        
        assert result is None


class TestSparqlQueryEscape:
    """SPARQLエスケープ機能のテスト"""

    def test_escape_double_quotes(self, graph_with_data):
        """ダブルクォートを含むタイトル検索がエラーにならないテスト"""
        sq = SparqlQuery(graph_with_data)
        
        # ダブルクォートを含む検索でもエラーにならないこと
        results = sq.search(paper_title='Test "quoted" title')
        
        # 結果は0件でも良いが、エラーが発生しないことが重要
        assert isinstance(results, list)

    def test_escape_backslashes(self, graph_with_data):
        """バックスラッシュを含むタイトル検索がエラーにならないテスト"""
        sq = SparqlQuery(graph_with_data)
        
        results = sq.search(paper_title='C:\\path\\to\\file')
        
        assert isinstance(results, list)

    def test_escape_special_chars_combined(self, graph_with_data):
        """複数の特殊文字を含むタイトル検索がエラーにならないテスト"""
        sq = SparqlQuery(graph_with_data)
        
        results = sq.search(paper_title='Test "quoted" and \\backslash')
        
        assert isinstance(results, list)


class TestSparqlQueryURIExperimentType:
    """URI形式のexperimentTypeフィルタのテスト"""

    def test_search_by_uri_experiment_type(self, graph_with_data):
        """kg:Synthesis形式の実験タイプでフィルタ検索するテスト"""
        sq = SparqlQuery(graph_with_data)
        
        # UIからはkg:Synthesis形式で来る
        results = sq.search(experiment_type="kg:Synthesis")
        
        assert len(results) == 1
        assert "Synthesis" in results[0]["experiment_type"]

    def test_search_by_uri_experiment_type_electrochemical(self, graph_with_data):
        """kg:Electrochemical形式の実験タイプでフィルタ検索するテスト"""
        sq = SparqlQuery(graph_with_data)
        
        results = sq.search(experiment_type="kg:Electrochemical")
        
        assert len(results) == 1
        assert "Electrochemical" in results[0]["experiment_type"]
