# Fixed Plan for KGpaper Improvements

## Architecture
- **Session State**: Explicitly check for key existence to prevent stale state errors.
- **Resource Management**: Robust cleanup in `LLMExtractor` ensures no orphaned files on Gemini.
- **Performance**: `GraphManager` singleton pattern via Streamlit caching.

## Key Changes
1. `ui/pages/2_manage.py`: Safe dictionary access for `papers_to_delete`.
2. `src/kgpaper/llm_extractor.py`:
    - `upload_file`: Internal try/except for cleanup on timeout.
    - `extract_from_file`: Move uploads into try/finally block.
3. `src/kgpaper/utils.py` (New): `get_graph_manager` function with `@st.cache_resource`.
4. Update all UI pages to use `get_graph_manager()`.