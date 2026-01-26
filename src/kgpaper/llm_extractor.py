import os
import json
import time
from pathlib import Path
from google import genai
from google.genai import types
from .config import load_config

class LLMExtractor:
    def __init__(self, config_path="config.yaml"):
        self.config = load_config(config_path)
        self.client = genai.Client(api_key=self.config.api_key)
        
    def _read_prompt(self) -> str:
        prompt_path = Path(self.config.prompt_path)
        if not prompt_path.exists():
            # Try relative to project root if not absolute/found
            # Assuming cwd is project root usually
            prompt_path = Path(os.getcwd()) / self.config.prompt_path
            
        if not prompt_path.exists():
             raise FileNotFoundError(f"Prompt file not found at {prompt_path}")
             
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def upload_file(self, file_path: str):
        """Uploads a file to Gemini API."""
        file = self.client.files.upload(path=file_path)
        print(f"Uploaded file: {file.name} ({file.uri})")
        
        # Wait for processing state if necessary (usually 'ACTIVE')
        while file.state.name == "PROCESSING":
            print("Processing file...")
            time.sleep(2)
            file = self.client.files.get(name=file.name)
            
        if file.state.name != "ACTIVE":
             raise Exception(f"File upload failed with state: {file.state.name}")
             
        return file

    def extract_json_ld(self, file_path: str, document_type: str = "main") -> dict:
        """
        Extracts JSON-LD from the given PDF file using Gemini.
        Returns a dict representing the JSON-LD.
        """
        prompt_text = self._read_prompt()
        
        # Inject context info if needed, e.g. filename
        filename = os.path.basename(file_path)
        prompt_text += f"\n\nContext Information:\nSource Filename: {filename}\nDocument Type: {document_type}\n"
        
        uploaded_file = self.upload_file(file_path)
        
        try:
            response = self.client.models.generate_content(
                model=self.config.gemini_model,
                contents=[uploaded_file, prompt_text],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
                
            return json.loads(response.text)
            
        finally:
            # Cleanup: Delete file from Gemini storage to save space/privacy
            # Note: In production might want to keep it purely transient or managed
            try:
                self.client.files.delete(name=uploaded_file.name)
                print(f"Deleted file resource: {uploaded_file.name}")
            except Exception as e:
                print(f"Warning: Failed to delete file {uploaded_file.name}: {e}")

