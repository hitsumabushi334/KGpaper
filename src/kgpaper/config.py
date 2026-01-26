import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AppConfig:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            
        return config

    @property
    def gemini_model(self) -> str:
        return self.config.get("gemini", {}).get("model", "gemini-2.0-flash")
    
    @property
    def api_key(self) -> str:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
             # Fallback or warning, but better to return None or raise error later if needed
             pass
        return api_key

    @property
    def prompt_path(self) -> str:
        return self.config.get("prompt", {}).get("extraction", "prompts/extraction_prompt.md")

    @property
    def graph_dir(self) -> Path:
        path_str = self.config.get("storage", {}).get("graph_dir", "data/graphs")
        return Path(path_str)

    @property
    def default_format(self) -> str:
        return self.config.get("storage", {}).get("default_format", "json-ld")

# Global config instance can be initialized here or in main app
def load_config(path: str = "config.yaml") -> AppConfig:
    return AppConfig(path)
