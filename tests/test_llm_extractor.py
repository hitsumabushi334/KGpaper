"""
llm_extractor.py のテスト

LLMExtractor クラスのテストを実施する。
Gemini APIはモックを使用してテストする。
"""
import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestLLMExtractorInit:
    """LLMExtractor.__init__ のテスト"""

    def test_init_creates_client(self, tmp_path, monkeypatch):
        """初期化時にGemini Clientが作成されるテスト"""
        # 設定ファイルを作成
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "prompts/extraction_prompt.md"
storage:
  graph_dir: "data/graphs"
""", encoding="utf-8")
        
        # 環境変数を設定
        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
        
        # genai.Client をモック
        with patch("kgpaper.llm_extractor.genai.Client") as mock_client:
            from kgpaper.llm_extractor import LLMExtractor
            
            extractor = LLMExtractor(config_path=str(config_file))
            
            mock_client.assert_called_once_with(api_key="test-api-key")
            assert extractor.config is not None


class TestLLMExtractorReadPrompt:
    """LLMExtractor._read_prompt のテスト"""

    def test_read_prompt_exists_at_direct_path(self, tmp_path, monkeypatch):
        """プロンプトファイルが直接パスで見つかる場合のテスト"""
        # 設定ファイルを作成
        config_file = tmp_path / "config.yaml"
        prompt_file = tmp_path / "prompt.md"
        prompt_file.write_text("Test prompt content", encoding="utf-8")
        
        config_file.write_text(f"""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "{str(prompt_file).replace(os.sep, '/')}"
storage:
  graph_dir: "data/graphs"
""", encoding="utf-8")
        
        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
        
        with patch("kgpaper.llm_extractor.genai.Client"):
            from kgpaper.llm_extractor import LLMExtractor
            
            extractor = LLMExtractor(config_path=str(config_file))
            result = extractor._read_prompt()
            
            assert result == "Test prompt content"

    def test_read_prompt_exists_at_cwd_relative(self, tmp_path, monkeypatch):
        """プロンプトファイルがcwd相対パスで見つかる場合のテスト"""
        # 設定ファイルを作成
        config_file = tmp_path / "config.yaml"
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        prompt_file = prompts_dir / "extraction_prompt.md"
        prompt_file.write_text("CWD relative prompt", encoding="utf-8")
        
        config_file.write_text("""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "prompts/extraction_prompt.md"
storage:
  graph_dir: "data/graphs"
""", encoding="utf-8")
        
        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
        
        # カレントディレクトリを一時ディレクトリに変更
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            with patch("kgpaper.llm_extractor.genai.Client"):
                from kgpaper.llm_extractor import LLMExtractor
                
                extractor = LLMExtractor(config_path=str(config_file))
                result = extractor._read_prompt()
                
                assert result == "CWD relative prompt"
        finally:
            os.chdir(original_cwd)

    def test_read_prompt_file_not_found(self, tmp_path, monkeypatch):
        """プロンプトファイルが見つからない場合のFileNotFoundErrorテスト"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "nonexistent/prompt.md"
storage:
  graph_dir: "data/graphs"
""", encoding="utf-8")
        
        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
        
        with patch("kgpaper.llm_extractor.genai.Client"):
            from kgpaper.llm_extractor import LLMExtractor
            
            extractor = LLMExtractor(config_path=str(config_file))
            
            with pytest.raises(FileNotFoundError) as exc_info:
                extractor._read_prompt()
            
            assert "Prompt file not found" in str(exc_info.value)


class TestLLMExtractorUploadFile:
    """LLMExtractor.upload_file のテスト"""

    def test_upload_file_success_active(self, tmp_path, monkeypatch, capsys):
        """ファイルアップロード成功（すぐにACTIVE状態）のテスト"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "prompt.md"
storage:
  graph_dir: "data/graphs"
""", encoding="utf-8")
        
        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
        
        # ファイル状態のモック
        mock_file = Mock()
        mock_file.name = "test-file-name"
        mock_file.uri = "gs://test-uri"
        mock_file.state.name = "ACTIVE"
        
        mock_client = Mock()
        mock_client.files.upload.return_value = mock_file
        
        with patch("kgpaper.llm_extractor.genai.Client", return_value=mock_client):
            from kgpaper.llm_extractor import LLMExtractor
            
            extractor = LLMExtractor(config_path=str(config_file))
            result = extractor.upload_file("test.pdf")
            
            assert result == mock_file
            mock_client.files.upload.assert_called_once_with(path="test.pdf")
            
            captured = capsys.readouterr()
            assert "Uploaded file: test-file-name" in captured.out

    def test_upload_file_processing_then_active(self, tmp_path, monkeypatch, capsys):
        """ファイルアップロード中にPROCESSING状態からACTIVEに遷移するテスト"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "prompt.md"
storage:
  graph_dir: "data/graphs"
""", encoding="utf-8")
        
        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
        
        # 最初はPROCESSING、次にACTIVE
        mock_state_processing = Mock()
        mock_state_processing.name = "PROCESSING"
        
        mock_state_active = Mock()
        mock_state_active.name = "ACTIVE"
        
        mock_file_processing = Mock()
        mock_file_processing.name = "test-file"
        mock_file_processing.uri = "gs://test"
        mock_file_processing.state = mock_state_processing
        
        mock_file_active = Mock()
        mock_file_active.name = "test-file"
        mock_file_active.uri = "gs://test"
        mock_file_active.state = mock_state_active
        
        mock_client = Mock()
        mock_client.files.upload.return_value = mock_file_processing
        mock_client.files.get.return_value = mock_file_active
        
        with patch("kgpaper.llm_extractor.genai.Client", return_value=mock_client):
            with patch("kgpaper.llm_extractor.time.sleep"):  # sleepをスキップ
                from kgpaper.llm_extractor import LLMExtractor
                
                extractor = LLMExtractor(config_path=str(config_file))
                result = extractor.upload_file("test.pdf")
                
                assert result.state.name == "ACTIVE"
                
                captured = capsys.readouterr()
                assert "Processing file..." in captured.out

    def test_upload_file_failed_state(self, tmp_path, monkeypatch):
        """ファイルアップロード失敗（FAILED状態）のテスト"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "prompt.md"
storage:
  graph_dir: "data/graphs"
""", encoding="utf-8")
        
        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
        
        mock_state = Mock()
        mock_state.name = "FAILED"
        
        mock_file = Mock()
        mock_file.name = "test-file"
        mock_file.uri = "gs://test"
        mock_file.state = mock_state
        
        mock_client = Mock()
        mock_client.files.upload.return_value = mock_file
        
        with patch("kgpaper.llm_extractor.genai.Client", return_value=mock_client):
            from kgpaper.llm_extractor import LLMExtractor
            
            extractor = LLMExtractor(config_path=str(config_file))
            
            with pytest.raises(Exception) as exc_info:
                extractor.upload_file("test.pdf")
            
            assert "File upload failed with state: FAILED" in str(exc_info.value)


class TestLLMExtractorExtractJsonLd:
    """LLMExtractor.extract_json_ld のテスト"""

    def test_extract_json_ld_success(self, tmp_path, monkeypatch, capsys):
        """JSON-LD抽出成功のテスト"""
        config_file = tmp_path / "config.yaml"
        prompt_file = tmp_path / "prompt.md"
        prompt_file.write_text("Extract JSON-LD", encoding="utf-8")
        
        config_file.write_text(f"""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "{str(prompt_file).replace(os.sep, '/')}"
storage:
  graph_dir: "data/graphs"
""", encoding="utf-8")
        
        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
        
        # モックのセットアップ
        mock_state = Mock()
        mock_state.name = "ACTIVE"
        
        mock_file = Mock()
        mock_file.name = "uploaded-file"
        mock_file.uri = "gs://test"
        mock_file.state = mock_state
        
        mock_response = Mock()
        mock_response.text = '{"@context": {}, "@id": "urn:test"}'
        
        mock_client = Mock()
        mock_client.files.upload.return_value = mock_file
        mock_client.models.generate_content.return_value = mock_response
        mock_client.files.delete.return_value = None
        
        with patch("kgpaper.llm_extractor.genai.Client", return_value=mock_client):
            with patch("kgpaper.llm_extractor.types"):
                from kgpaper.llm_extractor import LLMExtractor
                
                extractor = LLMExtractor(config_path=str(config_file))
                result = extractor.extract_json_ld("test.pdf", document_type="main")
                
                assert result == {"@context": {}, "@id": "urn:test"}
                
                # ファイルの削除が呼ばれたことを確認
                mock_client.files.delete.assert_called_once_with(name="uploaded-file")
                
                captured = capsys.readouterr()
                assert "Deleted file resource" in captured.out

    def test_extract_json_ld_empty_response(self, tmp_path, monkeypatch):
        """空のレスポンスでValueErrorが発生するテスト"""
        config_file = tmp_path / "config.yaml"
        prompt_file = tmp_path / "prompt.md"
        prompt_file.write_text("Extract JSON-LD", encoding="utf-8")
        
        config_file.write_text(f"""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "{str(prompt_file).replace(os.sep, '/')}"
storage:
  graph_dir: "data/graphs"
""", encoding="utf-8")
        
        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
        
        mock_state = Mock()
        mock_state.name = "ACTIVE"
        
        mock_file = Mock()
        mock_file.name = "uploaded-file"
        mock_file.uri = "gs://test"
        mock_file.state = mock_state
        
        mock_response = Mock()
        mock_response.text = ""  # 空のレスポンス
        
        mock_client = Mock()
        mock_client.files.upload.return_value = mock_file
        mock_client.models.generate_content.return_value = mock_response
        
        with patch("kgpaper.llm_extractor.genai.Client", return_value=mock_client):
            with patch("kgpaper.llm_extractor.types"):
                from kgpaper.llm_extractor import LLMExtractor
                
                extractor = LLMExtractor(config_path=str(config_file))
                
                with pytest.raises(ValueError) as exc_info:
                    extractor.extract_json_ld("test.pdf")
                
                assert "Empty response from Gemini" in str(exc_info.value)

    def test_extract_json_ld_cleanup_failure(self, tmp_path, monkeypatch, capsys):
        """ファイル削除（クリーンアップ）失敗時の警告テスト"""
        config_file = tmp_path / "config.yaml"
        prompt_file = tmp_path / "prompt.md"
        prompt_file.write_text("Extract JSON-LD", encoding="utf-8")
        
        config_file.write_text(f"""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "{str(prompt_file).replace(os.sep, '/')}"
storage:
  graph_dir: "data/graphs"
""", encoding="utf-8")
        
        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
        
        mock_state = Mock()
        mock_state.name = "ACTIVE"
        
        mock_file = Mock()
        mock_file.name = "uploaded-file"
        mock_file.uri = "gs://test"
        mock_file.state = mock_state
        
        mock_response = Mock()
        mock_response.text = '{"@context": {}}'
        
        mock_client = Mock()
        mock_client.files.upload.return_value = mock_file
        mock_client.models.generate_content.return_value = mock_response
        mock_client.files.delete.side_effect = Exception("Delete failed")
        
        with patch("kgpaper.llm_extractor.genai.Client", return_value=mock_client):
            with patch("kgpaper.llm_extractor.types"):
                from kgpaper.llm_extractor import LLMExtractor
                
                extractor = LLMExtractor(config_path=str(config_file))
                
                # エラーはraiseされずに結果が返される
                result = extractor.extract_json_ld("test.pdf")
                
                assert result == {"@context": {}}
                
                captured = capsys.readouterr()
                assert "Warning: Failed to delete file" in captured.out
