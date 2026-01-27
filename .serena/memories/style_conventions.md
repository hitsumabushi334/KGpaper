# コードスタイルと規約

## 言語設定

- **コメント**: 日本語で記述する
- **ドキュメント文字列**: 日本語で記述可

## Python コードスタイル

### 型ヒント

- 関数の引数と戻り値には型ヒントを付ける
- `Path` オブジェクトを適切に使用する

```python
def _load_config(self) -> dict:
    ...

@property
def graph_dir(self) -> Path:
    return Path(path_str)
```

### クラス設計

- プロパティデコレータを使用してゲッターを定義
- `__init__` でConfig/設定ファイルのパスを受け取る
- privateメソッドには `_` プレフィックスを使用

### 命名規則

- クラス: PascalCase (例: `GraphManager`, `LLMExtractor`)
- 関数/メソッド: snake_case (例: `load_config`, `add_json_ld`)
- 定数: UPPER_SNAKE_CASE (例: `KG`, `PROP_PAPER_TITLE`)
- プライベート: `_` プレフィックス (例: `_load_config`)

### インポート順序

1. 標準ライブラリ
2. サードパーティ
3. ローカルモジュール

```python
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
```

### テストスタイル

- pytest フィクスチャを使用
- テスト関数名: `test_<機能名>`
- 一時ディレクトリには `tmp_path` フィクスチャを使用

```python
@pytest.fixture
def graph_manager(tmp_path):
    ...

def test_add_json_ld(graph_manager):
    ...
```

## 設定ファイル

- `config.yaml`: アプリケーション設定
- `.env`: 機密情報 (API キー)
- 環境変数は `python-dotenv` で読み込み
