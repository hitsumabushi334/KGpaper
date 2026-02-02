import streamlit as st
from kgpaper.graph_manager import GraphManager


@st.cache_resource
def get_graph_manager(config_path="config.yaml"):
    """
    Returns a cached instance of GraphManager.
    This prevents reloading the graph on every Streamlit rerun.
    """
    return GraphManager(config_path=config_path)


def clear_graph_manager_cache():
    """
    Clears the cached GraphManager instance.
    Call this after adding/deleting data to ensure fresh data on next access.
    Also resets Explore page session state to force data refresh.
    """
    get_graph_manager.clear()
    # Exploreページのセッション状態もリセットして再読み込みを強制
    if "explore_initialized" in st.session_state:
        st.session_state.explore_initialized = False
    if "explore_results" in st.session_state:
        st.session_state.explore_results = None
