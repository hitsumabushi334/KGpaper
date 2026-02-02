import streamlit as st
import json
import pandas as pd
from st_cytoscape import cytoscape
from kgpaper.graph_manager import GraphManager
from kgpaper.sparql_query import SparqlQuery

st.set_page_config(page_title="Explore & Visualize", page_icon="🔍", layout="wide")
st.title("🔍 Explore Knowledge Graph")

gm = GraphManager()
sq = SparqlQuery(gm.g)

# session_stateの初期化
if "explore_results" not in st.session_state:
    st.session_state.explore_results = None
    st.session_state.explore_initialized = False

# message: filters
st.sidebar.header("Filters")

# 登録済み論文のタイトル一覧を取得
papers = gm.get_all_papers()
paper_titles = ["All"] + [p["title"] for p in papers]
paper_title_selected = st.sidebar.selectbox("Paper Title", paper_titles)
paper_title = paper_title_selected if paper_title_selected != "All" else None

document_type = st.sidebar.selectbox("Document Type", ["All", "main", "support"])
# Experiment TypeはURI形式（kg:Synthesis等）に対応
experiment_type = st.sidebar.selectbox(
    "Experiment Type",
    [
        "All",
        "kg:Synthesis",
        "kg:Characterization",
        "kg:Electrochemical",
        "kg:Spectroscopy",
        "kg:Thermal",
        "kg:Mechanical",
        "kg:Computational",
        "kg:Biological",
        "kg:Other",
    ],
)
content_type = st.sidebar.selectbox(
    "Content Type", ["All", "method", "result", "discussion", "conclusion"]
)

# 初回表示時に全件を検索（フィルターなし）
if not st.session_state.explore_initialized:
    st.session_state.explore_results = sq.search()
    st.session_state.explore_initialized = True

# Searchボタンクリック時はフィルター条件で再検索
if st.sidebar.button("Search", type="primary"):
    doc_type_filter = document_type if document_type != "All" else None
    experiment_type_filter = experiment_type if experiment_type != "All" else None
    content_type_filter = content_type if content_type != "All" else None

    st.session_state.explore_results = sq.search(
        paper_title=paper_title,
        document_type=doc_type_filter,
        experiment_type=experiment_type_filter,
        content_type=content_type_filter,
    )

# 結果の表示
results = st.session_state.explore_results
if not results:
    st.warning("No results found.")
else:
    st.subheader(f"Found {len(results)} items")

    # Display Data
    df = pd.DataFrame(results)
    # Select columns to display
    display_cols = ["paper_title", "experiment_type", "content_type", "text"]
    st.dataframe(df[display_cols], use_container_width=True)

    # Visualization
    st.subheader("Graph Visualization")

    # Convert results to Cytoscape elements
    elements = []
    nodes = set()
    edges = set()

    # Color mapping
    colors = {
        "method": "#4285F4",  # Blue
        "result": "#34A853",  # Green
        "discussion": "#FBBC04",  # Orange
        "conclusion": "#9C27B0",  # Purple
        "Paper": "#607D8B",  # Grey blue
        "Experiment": "#FF5722",  # Deep Orange
    }

    for item in results:
        p_uri = item["paper_uri"]
        p_title = item["paper_title"]
        e_uri = item["experiment_uri"]
        e_type = item["experiment_type"]
        c_uri = item["content_uri"]
        c_type = item["content_type"]
        text = item["text"]

        # Paper Node
        if p_uri not in nodes:
            # タイトルを最大30文字に制限
            p_label = p_title[:30] + "..." if len(p_title) > 30 else p_title
            elements.append(
                {
                    "data": {
                        "id": p_uri,
                        "label": p_label,
                        "full_title": p_title,
                        "type": "Paper",
                        "color": colors["Paper"],
                    }
                }
            )
            nodes.add(p_uri)

        # Experiment Node
        if e_uri not in nodes:
            elements.append(
                {
                    "data": {
                        "id": e_uri,
                        "label": e_type,
                        "type": "Experiment",
                        "color": colors["Experiment"],
                    }
                }
            )
            nodes.add(e_uri)

        # Content Node
        if c_uri not in nodes:
            # Truncate text for label
            label = text[:20] + "..." if len(text) > 20 else text
            color = colors.get(c_type, "#999999")
            elements.append(
                {
                    "data": {
                        "id": c_uri,
                        "label": label,
                        "type": c_type,
                        "color": color,
                        "full_text": text,
                    }
                }
            )
            nodes.add(c_uri)

        # Edges
        # Paper -> Experiment
        pe_edge = f"{p_uri}->{e_uri}"
        if pe_edge not in edges:
            elements.append(
                {"data": {"source": p_uri, "target": e_uri, "label": "hasExperiment"}}
            )
            edges.add(pe_edge)

        # Experiment -> Content
        ec_edge = f"{e_uri}->{c_uri}"
        if ec_edge not in edges:
            elements.append(
                {"data": {"source": e_uri, "target": c_uri, "label": "hasContent"}}
            )
            edges.add(ec_edge)

    # Style sheet
    stylesheet = [
        {
            "selector": "node",
            "style": {
                "label": "data(label)",
                "background-color": "data(color)",
                "width": 30,
                "height": 30,
                "font-size": 10,
                "text-valign": "center",
                "text-halign": "center",
                "color": "white",
                "text-outline-width": 1,
                "text-outline-color": "#333",
                "text-max-width": "100px",
                "text-wrap": "ellipsis",
            },
        },
        {
            "selector": "edge",
            "style": {
                "width": 2,
                "line-color": "#ccc",
                "target-arrow-color": "#ccc",
                "target-arrow-shape": "triangle",
                "curve-style": "bezier",
            },
        },
        {
            "selector": "node[type='Paper']",
            "style": {"width": 50, "height": 50, "font-size": 12},
        },
    ]

    # グラフ表示と選択状態の取得
    selected = cytoscape(
        elements,
        stylesheet,
        key="graph",
        layout={"name": "cose", "animate": True},
        height="600px",
        selection_type="single",
    )

    # 色凡例の表示
    st.markdown("### Node Colors Legend")
    legend_cols = st.columns(6)
    color_labels = {
        "Paper": ("論文", colors["Paper"]),
        "Experiment": ("実験", colors["Experiment"]),
        "method": ("手法", colors["method"]),
        "result": ("結果", colors["result"]),
        "discussion": ("考察", colors["discussion"]),
        "conclusion": ("結論", colors["conclusion"]),
    }
    for idx, (key, (lbl, clr)) in enumerate(color_labels.items()):
        with legend_cols[idx]:
            st.markdown(
                f'<div style="display:flex;align-items:center;">'
                f'<div style="width:16px;height:16px;background:{clr};'
                f'border-radius:4px;margin-right:8px;"></div>'
                f"<span>{lbl}</span></div>",
                unsafe_allow_html=True,
            )

    # 選択されたノードに関連するコンテンツをサブテーブルで表示
    if selected and selected.get("nodes"):
        selected_id = selected["nodes"][0]

        # 選択されたノードが所属する実験URIを特定
        target_experiment_uri = None
        for item in results:
            if selected_id in [
                item["paper_uri"],
                item["experiment_uri"],
                item["content_uri"],
            ]:
                target_experiment_uri = item["experiment_uri"]
                break

        if target_experiment_uri:
            # 同一実験に属する全コンテンツをフィルタリング
            related_items = [
                item
                for item in results
                if item["experiment_uri"] == target_experiment_uri
            ]

            if related_items:
                st.subheader("📋 選択されたノードの関連コンテンツ")
                related_df = pd.DataFrame(related_items)
                # PaperNameを除外し、可読性を向上
                display_cols_sub = ["experiment_type", "content_type", "text"]
                st.dataframe(related_df[display_cols_sub], use_container_width=True)

    # Export
    st.subheader("Export")
    # 直接ダウンロードボタンを表示（2段階フローを削除）
    json_str = json.dumps(results, indent=2, ensure_ascii=False)
    st.download_button(
        label="Download Filtered Results (JSON)",
        data=json_str,
        file_name="results.json",
        mime="application/json",
    )
