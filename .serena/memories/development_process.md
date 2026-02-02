# 開発プロセスのルール

## 基本フロー

```
実装計画確認 → TDD (RED→GREEN→REFACTOR) → 統合テスト → 手動検証 → 完了報告
```

## 1. 実装計画フェーズ

1. 実装計画書（implementation_plan.md）を確認
2. タスクリストを作成（task.md）
3. 変更対象と検証方法を把握

## 2. TDD実装フェーズ

### RED（テスト作成）
- 新機能のテストを先に作成
- `uv run pytest tests/<テストファイル>.py -v` で失敗を確認
- 失敗理由が「機能未実装」であることを確認

### GREEN（実装）
- 最小限のコードでテストをパスさせる
- Serenaのシンボリック操作ツールを活用
  - `find_symbol` / `get_symbols_overview` で既存コード確認
  - `insert_after_symbol` / `replace_content` で編集

### REFACTOR（整理）
- 重複コードの削除
- 命名改善

## 3. 統合確認フェーズ

```powershell
uv run pytest -v
```

- 全テストがパスすること
- 既存機能が壊れていないこと

## 4. 検証フェーズ

### 自動テスト
- 計画書の Verification Plan に従う

### 手動検証（UI変更時）
- `browser_subagent` でブラウザ確認
- スクリーンショット取得

## 5. 完了フェーズ

1. ウォークスルー作成（walkthrough.md）
2. タスクリスト完了マーク
3. コミット（PRがある場合はプッシュ）

## 重要なルール

- **テストファースト**: 実装前に必ずテストを書く
- **Serena優先**: コード検索・編集にSerenaを活用
- **日本語コメント**: コード内コメントは日本語
- **検証必須**: 完了報告前に必ずテストと手動検証

## 使用するスキル

| スキル | 用途 |
|--------|------|
| `executing-plans` | 計画実行 |
| `test-driven-development` | TDD手順 |
| `serena-development` | コード操作 |
| `verification-before-completion` | 完了前検証 |

## ワークフロー

`/implement-from-plan` - 実装計画からTDDで実装
