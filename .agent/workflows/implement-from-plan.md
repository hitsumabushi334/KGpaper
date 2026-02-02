---
description: 実装計画書に基づいてTDDで機能を実装するワークフロー
---

# 実装計画実行ワークフロー

実装計画書（implementation_plan.md）に基づいて、TDDで機能を実装する手順。

---

## 1. 準備フェーズ

### 1.1 計画書の確認
- 実装計画書（implementation_plan.md）を読み込む
- 変更対象ファイルと変更内容を確認
- 検証計画（Verification Plan）を確認

### 1.2 Serenaプロジェクトの活性化
```
mcp_serena_activate_project でプロジェクトを有効化
mcp_serena_read_memory で必要なメモリを読み込む
```

### 1.3 タスクリストの作成
- `task.md` を artifacts ディレクトリに作成
- 計画書の各コンポーネントをチェックリスト化
- TDDのフェーズ（RED → GREEN → REFACTOR）を明記

---

## 2. TDD実装フェーズ

### 2.1 RED - テスト作成
// turbo
```powershell
# 新規テストファイルがある場合、作成してからテスト実行
uv run pytest tests/<テストファイル>.py -v
```

**確認事項:**
- テストが期待通りに失敗することを確認
- 失敗理由が「機能未実装」であることを確認

### 2.2 GREEN - 実装
- Serenaの `find_symbol` / `get_symbols_overview` で既存コードを確認
- `insert_after_symbol` / `replace_symbol_body` で実装
- または `replace_content` で柔軟な編集

// turbo
```powershell
uv run pytest tests/<テストファイル>.py -v
```

**確認事項:**
- 新規テストがすべてパスすること
- 既存テストが壊れていないこと

### 2.3 REFACTOR - 整理
- 重複コードの削除
- 命名の改善
- ヘルパー関数の抽出

---

## 3. 統合確認フェーズ

// turbo
```powershell
# 全テスト実行
uv run pytest -v
```

**確認事項:**
- 全テストがパスすること
- 警告がないこと（許容範囲の警告を除く）

---

## 4. 検証フェーズ

### 4.1 自動テスト
- 計画書の Verification Plan に従ってテスト実行

### 4.2 手動検証（UI変更がある場合）
```
browser_subagent でUIを確認
- 期待されるUI要素の表示確認
- 既存機能が動作することの確認
- スクリーンショットの取得
```

---

## 5. 完了フェーズ

### 5.1 ウォークスルー作成
- `walkthrough.md` を artifacts ディレクトリに作成
- 変更内容のサマリー
- テスト結果
- スクリーンショット（UI変更がある場合）

### 5.2 タスクリスト更新
- すべてのチェックボックスを完了にマーク

### 5.3 コミット
```powershell
git add .
git commit -m "機能の説明"
```

---

## チェックリスト

実装完了時に確認:

- [ ] 全テストがパスしている
- [ ] 新機能のテストが追加されている
- [ ] TDDで実装された（テストが先に書かれた）
- [ ] コメントは日本語で記述されている
- [ ] UI変更がある場合、手動検証済み
- [ ] ウォークスルーが作成されている

---

## スキル参照

このワークフローで使用するスキル:

| スキル | 用途 |
|--------|------|
| `executing-plans` | 計画書の実行 |
| `test-driven-development` | TDDの手順 |
| `serena-development` | コード検索・編集 |
| `verification-before-completion` | 完了前の検証 |
