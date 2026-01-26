import streamlit as st
from kgpaper.graph_manager import GraphManager

st.set_page_config(page_title="Manage Data", page_icon="🗑️")
st.title("🗑️ Manage Data")

gm = GraphManager()
papers = gm.get_all_papers()

st.subheader("Registered Papers")

if not papers:
    st.info("No papers registered yet.")
else:
    # Display as a dataframe or list
    import pandas as pd
    df = pd.DataFrame(papers)
    st.dataframe(df, use_container_width=True)
    
    st.subheader("Delete Papers")
    
    # Selection for deletion
    paper_options = {p["title"] + f" ({p['uri']})": p["uri"] for p in papers}
    selected_papers = st.multiselect("Select papers to delete", options=list(paper_options.keys()))
    
    if st.button("Delete Selected", type="primary"):
        if selected_papers:
            for label in selected_papers:
                uri = paper_options[label]
                gm.delete_paper(uri)
                st.toast(f"Deleted {label}")
            st.rerun()

st.markdown("---")
st.subheader("Danger Zone")

if st.button("Clear All Data", type="primary"):
    # Confirmation dialog workaround
    if "confirm_clear" not in st.session_state:
        st.session_state.confirm_clear = True
        st.warning("Are you sure? This will delete all knowledge graph data. Click again to confirm.")
    else:
        gm.clear_all()
        st.success("All data cleared.")
        del st.session_state.confirm_clear
        st.rerun()
