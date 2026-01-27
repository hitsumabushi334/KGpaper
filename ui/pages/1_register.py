import streamlit as st
import tempfile
import os
from kgpaper.llm_extractor import LLMExtractor
from kgpaper.graph_manager import GraphManager

def validate_json_ld(json_ld: dict) -> tuple[bool, str]:
    """JSON-LDの構造を検証する"""
    if not isinstance(json_ld, dict):
        return False, "JSON-LDデータが辞書形式ではありません"
    if "@context" not in json_ld:
        return False, "@contextが見つかりません"
    if "@type" not in json_ld:
        return False, "@typeが見つかりません"
    return True, ""

st.set_page_config(page_title="Register Papers", page_icon="📝")

st.title("📝 Register Papers")

tab1, tab2 = st.tabs(["PDF Extract", "Import RDF"])

with tab1:
    st.header("Extract from PDF")
    uploaded_files = st.file_uploader(
        "Upload Paper PDFs", 
        type=["pdf"], 
        accept_multiple_files=True
    )
    
    document_type = st.selectbox("Document Type", ["main", "support"], index=0)
    
    if st.button("Start Extraction", type="primary", disabled=not uploaded_files):
        extractor = LLMExtractor()
        gm = GraphManager()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, file in enumerate(uploaded_files):
            status_text.text(f"Processing {file.name}...")
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.getvalue())
                tmp_path = tmp.name
                
            try:
                # st.statusで詳細な進捗を表示
                with st.status(f"Extracting from {file.name}...", expanded=True) as status:
                    st.write("📤 Uploading file to Gemini...")
                    
                    # Extract with progress callback
                    def update_progress(retry_count, elapsed):
                        st.write(f"⏳ Processing... (retry {retry_count}, {elapsed:.0f}s elapsed)")
                    
                    json_ld = extractor.extract_json_ld(tmp_path, document_type=document_type)

                    # バリデーション
                    is_valid, error_msg = validate_json_ld(json_ld)
                    if not is_valid:
                        st.error(f"JSON-LD構造エラー: {error_msg}")
                        status.update(label=f"⚠️ {file.name} failed", state="error")
                        continue

                    st.write("✅ Extraction complete!")
                    status.update(label=f"✅ {file.name} processed", state="complete")
                
                # Add source file metadata if not present
                if isinstance(json_ld, dict):
                    json_ld["sourceFile"] = file.name
                    if document_type == "support":
                        json_ld["documentType"] = "support"
                    else:
                        json_ld["documentType"] = "main"

                # Add to Graph
                gm.add_json_ld(json_ld)
                st.success(f"Successfully processed: {file.name}")
                
            except TimeoutError as e:
                st.error(f"⏰ Timeout processing {file.name}: {e}")
            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")
            finally:
                os.unlink(tmp_path)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
            
        status_text.text("All files processed!")

with tab2:
    st.header("Import Existing RDF")
    uploaded_rdf = st.file_uploader(
        "Upload RDF File (.ttl, .jsonld)", 
        type=["ttl", "json", "jsonld", "xml"]
    )
    
    if st.button("Import Graph"):
        if uploaded_rdf:
            gm = GraphManager()
            
            # Save to temp
            suffix = "." + uploaded_rdf.name.split(".")[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_rdf.getvalue())
                tmp_path = tmp.name
                
            try:
                gm.import_graph(tmp_path)
                st.success(f"Imported {uploaded_rdf.name}")
            except Exception as e:
                st.error(f"Import failed: {e}")
            finally:
                os.unlink(tmp_path)
