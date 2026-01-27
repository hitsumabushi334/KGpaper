# KGpaper プロジェクト概要

## プロジェクト目的
KGpaperは、複数の研究論文PDFから実験情報を抽出し、コンテキストを保持したナレッジグラフ（Knowledge Graph）を構築するアプリケーションです。

## 主な機能
- **Register**: PDFのアップロードと情報抽出、外部RDFのインポート
- **Manage**: 登録済み論文の管理・削除
- **Explore**: ナレッジグラフの検索と可視化

## 技術スタック
- **Python 3.12+** (uv パッケージマネージャー使用)
- **google-genai**: LLMによる論文情報抽出 (Gemini API)
- **rdflib**: RDFグラフ操作・SPARQL クエリ
- **Streamlit**: WebアプリケーションUI
- **st-cytoscape**: グラフ可視化
- **Pydantic**: データバリデーション
- **PyYAML**: 設定ファイル管理
- **pytest**: テストフレームワーク

## プロジェクト構造
```
KGpaper/
├── src/kgpaper/           # メインパッケージ
│   ├── config.py          # 設定管理クラス (AppConfig)
│   ├── graph_manager.py   # RDFグラフ管理 (GraphManager)
│   ├── llm_extractor.py   # LLM抽出 (LLMExtractor)
│   ├── ontology.py        # オントロジー定義 (定数、プレフィックス)
│   └── sparql_query.py    # SPARQL クエリ (SparqlQuery)
├── ui/                    # Streamlit UI
│   ├── app.py             # メインアプリ
│   └── pages/             # マルチページ
│       ├── 1_register.py
│       ├── 2_manage.py
│       └── 3_explore.py
├── tests/                 # テスト
├── prompts/               # LLM抽出用プロンプト
├── data/                  # データ保存
├── config.yaml            # アプリ設定ファイル
├── .env                   # 環境変数 (GOOGLE_API_KEY)
└── pyproject.toml         # プロジェクト定義
```

## 主要クラス
- **AppConfig**: YAML設定とenv変数を読み込む設定管理
- **GraphManager**: RDFグラフの読み書き、JSON-LDインポート、論文削除
- **LLMExtractor**: Google GenAI を使ってPDFから情報抽出
- **SparqlQuery**: グラフへのSPARQL検索
