"""
LLMExtractor.extract_json_ld_pair のテスト

MainファイルとSupportファイルをペアで処理する機能のテスト。
Gemini APIはモックを使用してテストする。
"""

import pytest
import os
from unittest.mock import Mock, patch


class TestLLMExtractorExtractJsonLdPair:
    """LLMExtractor.extract_json_ld_pair のテスト"""

    def test_extract_json_ld_pair_with_both_files(self, tmp_path, monkeypatch, capsys):
        """MainとSupport両方のファイルを渡した場合のテスト"""
        config_file = tmp_path / "config.yaml"
        prompt_file = tmp_path / "prompt.md"
        prompt_file.write_text("Extract JSON-LD", encoding="utf-8")

        config_file.write_text(
            f"""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "{str(prompt_file).replace(os.sep, '/')}"
storage:
  graph_dir: "data/graphs"
""",
            encoding="utf-8",
        )

        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")

        # テスト用PDFファイルを作成
        main_pdf = tmp_path / "main_paper.pdf"
        support_pdf = tmp_path / "support_si.pdf"
        main_pdf.write_bytes(b"%PDF-1.4 dummy main")
        support_pdf.write_bytes(b"%PDF-1.4 dummy support")

        # モックのセットアップ
        mock_state = Mock()
        mock_state.name = "ACTIVE"

        mock_main_file = Mock()
        mock_main_file.name = "main-file"
        mock_main_file.uri = "gs://main"
        mock_main_file.state = mock_state

        mock_support_file = Mock()
        mock_support_file.name = "support-file"
        mock_support_file.uri = "gs://support"
        mock_support_file.state = mock_state

        mock_response = Mock()
        mock_response.text = (
            '{"@context": {}, "@id": "urn:test", "documentType": "main"}'
        )

        mock_client = Mock()
        # 2回のupload呼び出しに対応
        mock_client.files.upload.side_effect = [mock_main_file, mock_support_file]
        mock_client.models.generate_content.return_value = mock_response
        mock_client.files.delete.return_value = None

        with patch("kgpaper.llm_extractor.genai.Client", return_value=mock_client):
            with patch("kgpaper.llm_extractor.types"):
                from kgpaper.llm_extractor import LLMExtractor

                extractor = LLMExtractor(config_path=str(config_file))
                result = extractor.extract_json_ld_pair(
                    main_file_path=str(main_pdf), support_file_path=str(support_pdf)
                )

                assert result == {
                    "@context": {},
                    "@id": "urn:test",
                    "documentType": "main",
                }

                # 2つのファイルがアップロードされたことを確認
                assert mock_client.files.upload.call_count == 2

                # 2つのファイルが削除されたことを確認
                assert mock_client.files.delete.call_count == 2

    def test_extract_json_ld_pair_main_only(self, tmp_path, monkeypatch, capsys):
        """Mainのみを渡した場合（Supportはオプション）のテスト"""
        config_file = tmp_path / "config.yaml"
        prompt_file = tmp_path / "prompt.md"
        prompt_file.write_text("Extract JSON-LD", encoding="utf-8")

        config_file.write_text(
            f"""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "{str(prompt_file).replace(os.sep, '/')}"
storage:
  graph_dir: "data/graphs"
""",
            encoding="utf-8",
        )

        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")

        # テスト用PDFファイルを作成（Mainのみ）
        main_pdf = tmp_path / "main_paper.pdf"
        main_pdf.write_bytes(b"%PDF-1.4 dummy main")

        # モックのセットアップ
        mock_state = Mock()
        mock_state.name = "ACTIVE"

        mock_main_file = Mock()
        mock_main_file.name = "main-file"
        mock_main_file.uri = "gs://main"
        mock_main_file.state = mock_state

        mock_response = Mock()
        mock_response.text = '{"@context": {}, "@id": "urn:test"}'

        mock_client = Mock()
        mock_client.files.upload.return_value = mock_main_file
        mock_client.models.generate_content.return_value = mock_response
        mock_client.files.delete.return_value = None

        with patch("kgpaper.llm_extractor.genai.Client", return_value=mock_client):
            with patch("kgpaper.llm_extractor.types"):
                from kgpaper.llm_extractor import LLMExtractor

                extractor = LLMExtractor(config_path=str(config_file))
                result = extractor.extract_json_ld_pair(
                    main_file_path=str(main_pdf), support_file_path=None  # Supportなし
                )

                assert result == {"@context": {}, "@id": "urn:test"}

                # 1つのファイルのみアップロードされたことを確認
                assert mock_client.files.upload.call_count == 1

                # 1つのファイルのみ削除されたことを確認
                assert mock_client.files.delete.call_count == 1

    def test_extract_json_ld_pair_prompt_includes_relationship_context(
        self, tmp_path, monkeypatch
    ):
        """プロンプトに本文とサポートの関係性が含まれることを確認するテスト"""
        config_file = tmp_path / "config.yaml"
        prompt_file = tmp_path / "prompt.md"
        prompt_file.write_text("Base prompt", encoding="utf-8")

        config_file.write_text(
            f"""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "{str(prompt_file).replace(os.sep, '/')}"
storage:
  graph_dir: "data/graphs"
""",
            encoding="utf-8",
        )

        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")

        # テスト用ファイルを作成
        main_pdf = tmp_path / "main.pdf"
        support_pdf = tmp_path / "support.pdf"
        main_pdf.write_bytes(b"%PDF-1.4 main")
        support_pdf.write_bytes(b"%PDF-1.4 support")

        # モックのセットアップ
        mock_state = Mock()
        mock_state.name = "ACTIVE"

        mock_file = Mock()
        mock_file.name = "file"
        mock_file.uri = "gs://file"
        mock_file.state = mock_state

        mock_response = Mock()
        mock_response.text = '{"@context": {}}'

        mock_client = Mock()
        mock_client.files.upload.return_value = mock_file
        mock_client.models.generate_content.return_value = mock_response
        mock_client.files.delete.return_value = None

        with patch("kgpaper.llm_extractor.genai.Client", return_value=mock_client):
            with patch("kgpaper.llm_extractor.types"):
                from kgpaper.llm_extractor import LLMExtractor

                extractor = LLMExtractor(config_path=str(config_file))
                extractor.extract_json_ld_pair(
                    main_file_path=str(main_pdf), support_file_path=str(support_pdf)
                )

                # generate_contentの呼び出し引数を取得
                call_args = mock_client.models.generate_content.call_args
                contents = call_args.kwargs.get("contents") or call_args[1].get(
                    "contents"
                )

                # contentsの最後の要素がプロンプト文字列
                prompt_text = contents[-1]

                # プロンプトに関係性の説明が含まれていることを確認
                assert (
                    "same research paper" in prompt_text.lower()
                    or "同じ論文" in prompt_text
                )
                assert "main" in prompt_text.lower()
                assert (
                    "support" in prompt_text.lower()
                    or "supplementary" in prompt_text.lower()
                )

    def test_extract_json_ld_pair_returns_valid_json_ld_structure(
        self, tmp_path, monkeypatch
    ):
        """返り値が有効なJSON-LD構造を持つことを確認するテスト"""
        config_file = tmp_path / "config.yaml"
        prompt_file = tmp_path / "prompt.md"
        prompt_file.write_text("Extract JSON-LD", encoding="utf-8")

        config_file.write_text(
            f"""
gemini:
  model: "gemini-2.0-flash"
prompt:
  extraction: "{str(prompt_file).replace(os.sep, '/')}"
storage:
  graph_dir: "data/graphs"
""",
            encoding="utf-8",
        )

        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")

        main_pdf = tmp_path / "main.pdf"
        main_pdf.write_bytes(b"%PDF-1.4 main")

        mock_state = Mock()
        mock_state.name = "ACTIVE"

        mock_file = Mock()
        mock_file.name = "file"
        mock_file.uri = "gs://file"
        mock_file.state = mock_state

        # 有効なJSON-LDレスポンス
        valid_json_ld = {
            "@context": {"schema": "https://schema.org/"},
            "@type": "ScholarlyArticle",
            "@id": "urn:paper:123",
        }

        mock_response = Mock()
        mock_response.text = '{"@context": {"schema": "https://schema.org/"}, "@type": "ScholarlyArticle", "@id": "urn:paper:123"}'

        mock_client = Mock()
        mock_client.files.upload.return_value = mock_file
        mock_client.models.generate_content.return_value = mock_response
        mock_client.files.delete.return_value = None

        with patch("kgpaper.llm_extractor.genai.Client", return_value=mock_client):
            with patch("kgpaper.llm_extractor.types"):
                from kgpaper.llm_extractor import LLMExtractor

                extractor = LLMExtractor(config_path=str(config_file))
                result = extractor.extract_json_ld_pair(
                    main_file_path=str(main_pdf), support_file_path=None
                )

                # JSON-LD構造の検証
                assert "@context" in result
                assert isinstance(result, dict)
