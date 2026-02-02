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

    def upload_file(self, file_path: str, progress_callback=None):
        """Uploads a file to Gemini API.

        Args:
            file_path: Path to the file to upload
            progress_callback: Optional callback function(retry_count, elapsed_seconds)
                               for progress reporting

        Raises:
            TimeoutError: If file processing exceeds timeout or max retries
            Exception: If file upload fails with an error state
        """
        file = self.client.files.upload(file=file_path)
        print(f"Uploaded file: {file.name} ({file.uri})")

        # Wait for processing state with timeout and retry limit
        timeout = self.config.upload_timeout
        max_retries = self.config.upload_max_retries
        start_time = time.time()
        retry_count = 0

        try:
            while file.state.name == "PROCESSING":
                elapsed = time.time() - start_time

                # 進捗コールバックを呼び出し
                if progress_callback:
                    progress_callback(retry_count, elapsed)

                # タイムアウトチェック
                if elapsed > timeout:
                    raise TimeoutError(
                        f"File processing timed out after {timeout} seconds"
                    )

                # リトライ回数チェック
                retry_count += 1
                if retry_count > max_retries:
                    raise TimeoutError(
                        f"File processing exceeded max retries ({max_retries}). "
                        f"File: {file.name}"
                    )

                print(f"Processing file... (retry {retry_count}/{max_retries})")
                time.sleep(2)
                file = self.client.files.get(name=file.name)

        except Exception:
            # 処理失敗時（タイムアウト含む）はファイルを削除
            try:
                self.client.files.delete(name=file.name)
                print(f"Deleted file due to processing failure: {file.name}")
            except Exception as e:
                print(f"Warning: Failed to delete file {file.name} during cleanup: {e}")
            raise

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
                ),
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

    def extract_json_ld_pair(
        self, main_file_path: str, support_file_path: str | None = None
    ) -> dict:
        """
        MainファイルとSupportファイルをペアで処理し、JSON-LDを抽出する。

        2つのファイルが同じ論文の本文（Main）とサポート資料（Support）の関係にあることを
        LLMに伝え、1回の呼び出しで両方を処理する。

        Args:
            main_file_path: 本文PDFのパス（必須）
            support_file_path: サポートPDFのパス（オプション）

        Returns:
            dict: 抽出されたJSON-LD
        """
        prompt_text = self._read_prompt()

        # アップロードするファイルのリスト
        uploaded_files = []

        try:
            # Mainファイルをアップロード
            main_uploaded = self.upload_file(main_file_path)
            uploaded_files.append(main_uploaded)
            main_filename = os.path.basename(main_file_path)

            support_uploaded = None
            support_filename = None

            # Supportファイルがある場合はアップロード
            if support_file_path:
                support_uploaded = self.upload_file(support_file_path)
                uploaded_files.append(support_uploaded)
                support_filename = os.path.basename(support_file_path)

            # プロンプトにコンテキスト情報を追加
            if support_file_path:
                # 2つのファイルがある場合、関係性を明記
                prompt_text += f"""

Context Information:
The following two files are from the same research paper.
- Main Article: {main_filename} (Document Type: main)
- Supplementary Material: {support_filename} (Document Type: support)

Please process both files together as a single research paper, extracting information from both the main article and supplementary material.
"""
                # contentsに両ファイルとプロンプトを含める
                contents = [main_uploaded, support_uploaded, prompt_text]
            else:
                # Mainのみの場合
                prompt_text += f"\n\nContext Information:\nSource Filename: {main_filename}\nDocument Type: main\n"
                contents = [main_uploaded, prompt_text]

            response = self.client.models.generate_content(
                model=self.config.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )

            if not response.text:
                raise ValueError("Empty response from Gemini")

            return json.loads(response.text)

        finally:
            # 全てのアップロードファイルを削除
            for uploaded_file in uploaded_files:
                try:
                    self.client.files.delete(name=uploaded_file.name)
                    print(f"Deleted file resource: {uploaded_file.name}")
                except Exception as e:
                    print(f"Warning: Failed to delete file {uploaded_file.name}: {e}")
