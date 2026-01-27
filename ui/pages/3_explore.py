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

# message: filters
st.sidebar.header("Filters")

# Fetch available distinct values for filters could be optimized, 
# but for now free text or defined enums
paper_title = st.sidebar.text_input("Paper Title")
document_type = st.sidebar.selectbox("Document Type", ["All", "main", "support"])
experiment_type = st.sidebar.selectbox("Experiment Type", [
    "All", "synthesis", "characterization", "electrochemical", "spectroscopy", 
    "thermal", "mechanical", "computational", "biological", "other"
])
content_type = st.sidebar.selectbox("Content Type", ["All", "method", "result", "discussion", "conclusion"])

if st.sidebar.button("Search", type="primary"):
    doc_type_filter = document_type if document_type != "All" else None
    experiment_type_filter = experiment_type if experiment_type != "All" else None
    content_type_filter = content_type if content_type != "All" else None
    
    results = sq.search(
        paper_title=paper_title,
        document_type=doc_type_filter,
        experiment_type=experiment_type_filter,
        content_type=content_type_filter
    )
    
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
            "method": "#4285F4",      # Blue
            "result": "#34A853",      # Green
            "discussion": "#FBBC04",  # Orange
            "conclusion": "#9C27B0",  # Purple
            "Paper": "#607D8B",       # Grey blue
            "Experiment": "#FF5722"   # Deep Orange
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
                elements.append({
                    "data": {"id": p_uri, "label": p_title, "type": "Paper", "color": colors["Paper"]}
                })
                nodes.add(p_uri)
                
            # Experiment Node
            if e_uri not in nodes:
                elements.append({
                    "data": {"id": e_uri, "label": e_type, "type": "Experiment", "color": colors["Experiment"]}
                })
                nodes.add(e_uri)
                
            # Content Node
            if c_uri not in nodes:
                # Truncate text for label
                label = text[:20] + "..." if len(text) > 20 else text
                color = colors.get(c_type, "#999999")
                elements.append({
                    "data": {"id": c_uri, "label": label, "type": c_type, "color": color, "full_text": text}
                })
                nodes.add(c_uri)
                
            # Edges
            # Paper -> Experiment
            pe_edge = f"{p_uri}->{e_uri}"
            if pe_edge not in edges:
                elements.append({"data": {"source": p_uri, "target": e_uri, "label": "hasExperiment"}})
                edges.add(pe_edge)
                
            # Experiment -> Content
            ec_edge = f"{e_uri}->{c_uri}"
            if ec_edge not in edges:
                elements.append({"data": {"source": e_uri, "target": c_uri, "label": "hasContent"}})
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
                    "text-outline-color": "#333"
                }
            },
            {
                "selector": "edge",
                "style": {
                    "width": 2,
                    "line-color": "#ccc",
                    "target-arrow-color": "#ccc",
                    "target-arrow-shape": "triangle",
                    "curve-style": "bezier"
                }
            },
            {
                "selector": "node[type='Paper']",
                "style": {"width": 50, "height": 50, "font-size": 12}
            }
        ]

        cytoscape(
            elements,
            stylesheet,
            key="graph",
            layout={"name": "cose", "animate": True},
            height="600px"
        )
        
        # Export
        st.subheader("Export")
        export_format = st.radio("Format", ["JSON-LD"])
        if st.button("Download Graph"):
            # フィルタ結果をJSONとしてエクスポート
            json_str = json.dumps(results, indent=2, ensure_ascii=False)
            st.download_button(
                label="Download Filtered Results (JSON)",
                data=json_str,
                file_name="results.json",
                mime="application/json"
            )
            
