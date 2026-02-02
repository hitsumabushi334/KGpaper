import streamlit as st
import sys
from pathlib import Path

# Add src to path for direct execution if package not installed (fallback)
# project_root = Path(__file__).parent.parent
# sys.path.append(str(project_root / "src"))

st.set_page_config(
    page_title="Paper Knowledge Graph",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Research Paper Knowledge Graph Builder")

st.markdown("""
### 概要
このアプリケーションは複数の研究論文PDFから実験情報を抽出し、
コンテキストを保持したナレッジグラフを構築します。

### 機能
- **Register**: PDFのアップロードと情報抽出、外部RDFのインポート
- **Manage**: 登録済み論文の管理・削除
- **Explore**: ナレッジグラフの検索と可視化

### 始め方
左側のサイドバーからページを選択してください。
""")
