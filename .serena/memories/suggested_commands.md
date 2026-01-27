# 推奨コマンド

## パッケージ管理 (uv)
```powershell
# 依存関係のインストール
uv sync

# 開発用依存関係も含めてインストール
uv sync --dev

# パッケージの追加
uv add <package-name>

# 開発用パッケージの追加
uv add --dev <package-name>
```

## アプリケーション実行
```powershell
# Streamlit UIの起動
uv run streamlit run ui/app.py

# または (パッケージインストール済みの場合)
streamlit run ui/app.py

# メインスクリプト実行
uv run python main.py
```

## テスト
```powershell
# テスト実行
uv run pytest

# カバレッジ付きテスト
uv run pytest --cov=src/kgpaper

# 特定のテストファイル実行
uv run pytest tests/test_graph_manager.py

# 詳細出力
uv run pytest -v
```

## Git コマンド (Windows)
```powershell
# ステータス確認
git status

# ブランチ作成・切り替え
git checkout -b <branch-name>

# コミット
git add .
git commit -m "コミットメッセージ"

# プッシュ
git push origin <branch-name>

# プルリクエスト作成 (GitHub CLI)
gh pr create --title "タイトル" --body "説明"
```

## ユーティリティ (PowerShell)
```powershell
# ディレクトリ一覧
Get-ChildItem  # または ls

# ファイル検索
Get-ChildItem -Recurse -Filter "*.py"

# パターン検索 (grep相当)
Select-String -Path "src/**/*.py" -Pattern "パターン"

# 現在のディレクトリ
Get-Location  # または pwd
```
