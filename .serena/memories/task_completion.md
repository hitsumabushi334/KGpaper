# タスク完了時の手順

## 1. コード変更後の確認

### テスト実行
```powershell
uv run pytest -v
```

### テストカバレッジ確認
```powershell
uv run pytest --cov=src/kgpaper
```

## 2. Git コミット

### ブランチでの作業 (TDD プロセス)
1. 機能ブランチに切り替え
   ```powershell
   git checkout -b feature/<機能名>
   ```

2. 変更をステージング
   ```powershell
   git add .
   ```

3. コミット (日本語可)
   ```powershell
   git commit -m "機能の説明"
   ```

## 3. プルリクエスト

### GitHub CLI でPR作成
```powershell
gh pr create --title "PRタイトル" --body "変更内容の説明"
```

### レビュー対応
- レビューコメントに基づき修正
- 修正後、追加コミット
- 承認後にマージ

## 4. マージ後

### mainブランチに戻る
```powershell
git checkout main
git pull origin main
```

### ローカルブランチの削除
```powershell
git branch -d feature/<機能名>
```

## チェックリスト
- [ ] 全テストがパスしている
- [ ] 型ヒントが適切に付けられている
- [ ] コメントは日本語で記述されている
- [ ] コードがTDDで実装されている（テストが過剰適応していないか確認）
- [ ] PRレビューで問題が指摘されていない
