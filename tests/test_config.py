"""
config.py のテスト

AppConfig クラスと load_config 関数のテストを実施する。
"""
import pytest
import os
from pathlib import Path
from kgpaper.config import AppConfig, load_config


class TestAppConfig:
    """AppConfig クラスのテスト"""

    def test_init_with_valid_config(self, tmp_path):
        """有効な設定ファイルでの初期化テスト"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
gemini:
  model: "gemini-2.0-flash"
storage:
  graph_dir: "data/graphs"
  default_format: "json-ld"
prompt:
  extraction: "prompts/extraction_prompt.md"
""", encoding="utf-8")
        
        config = AppConfig(str(config_file))
        
        assert config.gemini_model == "gemini-2.0-flash"
        assert config.graph_dir == Path("data/graphs")
        assert config.default_format == "json-ld"
        assert config.prompt_path == "prompts/extraction_prompt.md"

    def test_init_file_not_found(self, tmp_path):
        """存在しない設定ファイルで FileNotFoundError が発生するテスト"""
        non_existent_path = tmp_path / "non_existent.yaml"
        
        with pytest.raises(FileNotFoundError) as exc_info:
            AppConfig(str(non_existent_path))
        
        assert "Config file not found" in str(exc_info.value)

    def test_gemini_model_default(self, tmp_path):
        """gemini_model のデフォルト値テスト"""
        config_file = tmp_path / "config.yaml"
        # gemini セクションを空にしてデフォルト値をテスト
        config_file.write_text("storage:\n  graph_dir: test", encoding="utf-8")
        
        config = AppConfig(str(config_file))
        
        assert config.gemini_model == "gemini-2.0-flash"

    def test_prompt_path_default(self, tmp_path):
        """prompt_path のデフォルト値テスト"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("storage:\n  graph_dir: test", encoding="utf-8")
        
        config = AppConfig(str(config_file))
        
        assert config.prompt_path == "prompts/extraction_prompt.md"

    def test_graph_dir_default(self, tmp_path):
        """graph_dir のデフォルト値テスト"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("gemini:\n  model: test", encoding="utf-8")
        
        config = AppConfig(str(config_file))
        
        assert config.graph_dir == Path("data/graphs")

    def test_default_format_default(self, tmp_path):
        """default_format のデフォルト値テスト"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("gemini:\n  model: test", encoding="utf-8")
        
        config = AppConfig(str(config_file))
        
        assert config.default_format == "json-ld"

    def test_api_key_from_env(self, tmp_path, monkeypatch):
        """環境変数から api_key を取得するテスト"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("gemini:\n  model: test", encoding="utf-8")
        
        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key-12345")
        
        config = AppConfig(str(config_file))
        
        assert config.api_key == "test-api-key-12345"

    def test_api_key_missing(self, tmp_path, monkeypatch):
        """環境変数が設定されていない場合の api_key テスト"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("gemini:\n  model: test", encoding="utf-8")
        
        # 環境変数を削除
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        
        config = AppConfig(str(config_file))
        
        assert config.api_key is None


class TestLoadConfig:
    """load_config 関数のテスト"""

    def test_load_config_returns_appconfig(self, tmp_path):
        """load_config が AppConfig インスタンスを返すテスト"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("gemini:\n  model: test-model", encoding="utf-8")
        
        config = load_config(str(config_file))
        
        assert isinstance(config, AppConfig)
        assert config.gemini_model == "test-model"
