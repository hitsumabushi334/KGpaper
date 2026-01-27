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
    
    # Selection for deletion (固定キーを使用してボタン消失問題を回避)
    paper_options = {p["title"] + f" ({p['uri']})": p["uri"] for p in papers}
    selected_papers = st.multiselect(
        "Select papers to delete", 
        options=list(paper_options.keys()),
        key="papers_to_delete_selection"
    )
    
    # 確認状態でない場合のみDeleteボタンを表示
    if not st.session_state.get("confirm_delete_selected", False):
        if st.button("Delete Selected", type="primary", disabled=len(selected_papers) == 0):
            if selected_papers:
                st.session_state.confirm_delete_selected = True
                st.session_state.papers_to_delete = selected_papers
                st.rerun()
    
    # 確認ダイアログを表示
    if st.session_state.get("confirm_delete_selected", False):
        papers_to_delete = st.session_state.get("papers_to_delete", [])
        st.warning(f"⚠️ {len(papers_to_delete)}件の論文を削除します。この操作は元に戻せません。")
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("✓ 削除を確定", type="primary"):
                for label in papers_to_delete:
                    uri = paper_options[label]
                    gm.delete_paper(uri)
                    st.toast(f"Deleted {label}")
                st.session_state.pop("confirm_delete_selected", None)
                st.session_state.pop("papers_to_delete", None)
                st.rerun()
        with col_cancel:
            if st.button("✗ キャンセル"):
                st.session_state.pop("confirm_delete_selected", None)
                st.session_state.pop("papers_to_delete", None)
                st.rerun()

st.markdown("---")
st.subheader("Danger Zone")

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("Clear All Data", type="primary"):
        st.session_state.show_clear_confirm = True

with col2:
    if st.session_state.get("show_clear_confirm", False):
        confirm = st.checkbox("I confirm deletion of all data", key="confirm_clear_now")
        if confirm:
            if st.button("⚠️ Execute Delete", type="secondary"):
                gm.clear_all()
                st.success("All data cleared.")
                st.session_state.pop("show_clear_confirm", None)
                st.session_state.pop("confirm_clear_now", None)
                st.rerun()
