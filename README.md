# 📚 KGpaper - Research Paper Knowledge Graph Builder

研究論文PDFから実験情報を自動抽出し、ナレッジグラフとして構築・可視化するStreamlitアプリケーション

## 🎯 概要

KGpaperは、複数の研究論文PDFから実験情報（手法、結果、考察、結論）を自動抽出し、コンテキストを保持したナレッジグラフを構築します。Google Gemini APIを活用したLLMベースの情報抽出と、RDF/JSON-LD形式でのグラフ管理を特徴としています。

## ✨ 機能

| タブ | 機能 |
|------|------|
| **Register** | PDFのアップロードと情報抽出、外部RDFのインポート |
| **Manage** | 登録済み論文の管理・削除 |
| **Explore** | ナレッジグラフの検索と可視化（フィルタリング・グラフ表示） |

### 実験分類

論文から抽出される実験は以下のカテゴリに自動分類されます：

- **Synthesis**: 合成、作製、製造、培養、デバイス構築
- **Characterization**: 構造・組成分析（XRD, NMR, SEM, TEM, XPSなど）
- **Spectroscopy**: 光学的・分光的測定（UV-vis, FT-IR, PL, 過渡吸収など）
- **Electrochemical**: 電気化学的測定（CV, LSV, 電池性能, インピーダンスなど）
- **PerformanceTesting**: 実用性能、耐久性、変換効率、収率などの評価
- **Computational**: 理論計算、シミュレーション、機械学習モデル
- **Imaging**: 顕微鏡観察、非破壊検査、CT、トモグラフィー
- **Kinetic**: 反応速度論、経時変化測定、寿命測定
- **Thermodynamic**: 熱力学特性、相転移、吸着等温線（DSC, TGA, BET）
- **Mechanical**: 強度、硬度、弾性、摩擦特性
- **Biological**: 細胞試験、毒性評価、in-vivo/in-vitro 実験
- **Other**: その他

## 🛠️ 技術スタック

- **言語**: Python 3.12+
- **UI**: Streamlit
- **LLM**: Google Gemini API (`google-genai`)
- **グラフ**: RDFlib（JSON-LD形式）
- **可視化**: st-cytoscape

## 📦 インストール

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd KGpaper
```

### 2. uvを使用したインストール（推奨）

```bash
uv sync
```

### 3. 設定ファイルの作成

```bash
cp config_sample.yaml config.yaml
```

### 4. 環境変数の設定

`.env`ファイルを作成し、Gemini APIキーを設定：

```bash
GEMINI_API_KEY=your_api_key_here
```

## 🚀 起動方法

```bash
uv run streamlit run ui/app.py
```

ブラウザで `http://localhost:8501` を開いてアクセスしてください。

## 📁 プロジェクト構成

```
KGpaper/
├── src/kgpaper/           # コアライブラリ
│   ├── config.py          # 設定管理
│   ├── graph_manager.py   # RDFグラフ管理
│   ├── llm_extractor.py   # LLMによるPDF情報抽出
│   ├── ontology.py        # オントロジー定義
│   ├── sparql_query.py    # SPARQLクエリ
│   └── utils.py           # ユーティリティ
├── ui/                    # Streamlit UI
│   ├── app.py             # メインアプリ
│   └── pages/
│       ├── 1_register.py  # 論文登録ページ
│       ├── 2_manage.py    # 管理ページ
│       └── 3_explore.py   # 検索・可視化ページ
├── prompts/               # LLM用プロンプト
│   └── extraction_prompt.md
├── data/                  # データ保存ディレクトリ
│   └── graphs/            # RDFグラフファイル
├── tests/                 # テスト
├── config.yaml            # 設定ファイル
└── pyproject.toml         # プロジェクト設定
```

## 🧪 テスト

```bash
uv run pytest -v
```

## 📜 ライセンス

このプロジェクトはプライベートです。

## 🤝 貢献

貢献を歓迎します。Issue や Pull Request をお気軽にどうぞ。
