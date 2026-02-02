import streamlit as st
import tempfile
import os
from kgpaper.llm_extractor import LLMExtractor
from kgpaper.graph_manager import GraphManager
from kgpaper.utils import clear_graph_manager_cache


st.set_page_config(page_title="Register Papers", page_icon="📝")

st.title("📝 Register Papers")

tab1, tab2 = st.tabs(["PDF Extract", "Import RDF"])

with tab1:
    st.header("Extract from PDF")

    # 本文用アップローダー（必須、1ファイル限定）
    st.subheader("📄 Main Article (Required)")
    main_file = st.file_uploader("Upload Main PDF", type=["pdf"], key="main_uploader")

    # サポート用アップローダー（オプション、1ファイル限定）
    st.subheader("📎 Supplementary Material (Optional)")
    support_file = st.file_uploader(
        "Upload Support PDF", type=["pdf"], key="support_uploader"
    )

    # 抽出開始ボタン（本文ファイルが必須）
    if st.button("Start Extraction", type="primary", disabled=not main_file):
        extractor = LLMExtractor()
        gm = GraphManager()

        # 一時ファイルのパスを保持
        tmp_paths = []

        try:
            # 本文ファイルを一時保存
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(main_file.getvalue())
                main_tmp_path = tmp.name
                tmp_paths.append(main_tmp_path)

            # サポートファイルがあれば一時保存
            support_tmp_path = None
            if support_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(support_file.getvalue())
                    support_tmp_path = tmp.name
                    tmp_paths.append(support_tmp_path)

            # st.statusで進捗を表示
            files_desc = main_file.name
            if support_file:
                files_desc += f" + {support_file.name}"

            with st.status(f"Extracting from {files_desc}...", expanded=True) as status:
                st.write("📤 Uploading files to Gemini...")

                # ペア処理でJSON-LDを抽出
                json_ld = extractor.extract_json_ld_pair(
                    main_file_path=main_tmp_path, support_file_path=support_tmp_path
                )

                # バリデーション
                try:
                    GraphManager.validate_json_ld_structure(json_ld)
                except ValueError as e:
                    st.error(f"JSON-LD構造エラー: {e}")
                    status.update(label=f"⚠️ Extraction failed", state="error")
                else:
                    st.write("✅ Extraction complete!")
                    status.update(label=f"✅ Extraction complete", state="complete")

                    # ソースファイル情報を追加
                    if isinstance(json_ld, dict):
                        json_ld["sourceFile"] = main_file.name
                        json_ld["documentType"] = "main"
                        if support_file:
                            json_ld["supportFile"] = support_file.name

                    # グラフに追加
                    gm.add_json_ld(json_ld)
                    clear_graph_manager_cache()  # キャッシュをクリアして最新データを反映
                    st.success(f"Successfully processed: {files_desc}")

        except TimeoutError as e:
            st.error(f"⏰ Timeout: {e}")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            # 一時ファイルを削除
            for tmp_path in tmp_paths:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

with tab2:
    st.header("Import Existing RDF")
    uploaded_rdf = st.file_uploader(
        "Upload RDF File (.ttl, .jsonld)", type=["ttl", "json", "jsonld"]
    )

    if st.button("Import Graph"):
        if uploaded_rdf:
            from kgpaper.utils import get_graph_manager

            gm = get_graph_manager()

            # Save to temp
            suffix = "." + uploaded_rdf.name.split(".")[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_rdf.getvalue())
                tmp_path = tmp.name

            try:
                gm.import_graph(tmp_path)
                clear_graph_manager_cache()  # キャッシュをクリアして最新データを反映
                st.success(f"Imported {uploaded_rdf.name}")
            except Exception as e:
                st.error(f"Import failed: {e}")
            finally:
                os.unlink(tmp_path)
