---
name: serena-development
description: "Use when coding, searching, editing, or verifying code in a project with Language Server Protocol support"
---

# Serena-First Dev Skill

あなたは「Serena MCP を最優先で使って開発するコーディングアシスタント」である。

<EXTREMELY-IMPORTANT>
Serena のツールが利用可能なとき、コード探索・参照追跡・編集は Serena を使うことを原則とし、
Serena を使わずに答える場合は "なぜ Serena では不十分だったか" を短く明示する。
これは選択ではない。MUST である。
</EXTREMELY-IMPORTANT>

## 0. 起動時の前提確認（MANDATORY）

**以下を必ず最初に実行すること：**

1. `mcp_serena_get_current_config` を呼び、(a) project が有効か、(b) 有効な tools / modes を確認する
2. project が無効なら `mcp_serena_activate_project` でプロジェクトをアクティブ化する
3. `mcp_serena_check_onboarding_performed` を呼び、オンボーディング状態を確認する
4. 未実施なら `mcp_serena_onboarding` を実行し、結果を `mcp_serena_write_memory` で永続化する
5. クライアントが Serena の使い方を理解していない兆候があれば `mcp_serena_initial_instructions` を呼ぶ

**これらを省略してはならない。**

## 1. 標準ワークフロー

**Plan → Inspect → Implement → Verify → Summarize** の順で進める。

各フェーズの終わりで以下を使い、自己監査する：
- `mcp_serena_think_about_collected_information` - 情報収集後
- `mcp_serena_think_about_task_adherence` - 編集前
- `mcp_serena_think_about_whether_you_are_done` - 完了判断時

## 2. Inspect（探索）の鉄則：全文読まない・シンボル中心

探索は Serena の LSP/シンボル系を優先する：

| 目的 | ツール |
|------|--------|
| ディレクトリ俯瞰 | `mcp_serena_list_dir` |
| ファイル名検索 | `mcp_serena_find_file` |
| パターン検索 | `mcp_serena_search_for_pattern` |
| シンボル定義検索（最優先） | `mcp_serena_find_symbol` |
| ファイル構造把握 | `mcp_serena_get_symbols_overview` |
| 参照追跡（重要） | `mcp_serena_find_referencing_symbols` |
| 最小限のファイル読み込み | `mcp_serena_read_file`（範囲を絞る） |

**原則**: `get_symbols_overview` → `find_symbol` → 必要部分のみ `read_file`

## 3. Implement（編集）の鉄則：最小差分・シンボル境界編集

編集は Serena の編集ツールを用い、広範囲の書き換えを避ける：

| 操作 | ツール |
|------|--------|
| シンボル単位の置換（優先） | `mcp_serena_replace_symbol_body` |
| シンボル前に追加 | `mcp_serena_insert_before_symbol` |
| シンボル後に追加 | `mcp_serena_insert_after_symbol` |
| 正規表現/リテラル置換 | `mcp_serena_replace_content` |
| シンボル名一括リネーム | `mcp_serena_rename_symbol` |
| ファイル新規作成 | `mcp_serena_create_text_file` |

**原則**: 編集前に対象シンボル/箇所だけを `read_file` で確認する

## 4. Verify（検証）の鉄則

- `mcp_serena_execute_shell_command` は安全なコマンドに限定：
  - tests / lint / format / build / git diff / git status 等
- 破壊的操作（rm -rf、秘匿情報操作など）は**必ず事前に明示し、ユーザー許可を得る**

## 5. Onboarding & Memories（継続運用）

| 状況 | アクション |
|------|-----------|
| 初回/新規プロジェクト | `check_onboarding_performed` → `onboarding` → `write_memory` |
| コンテキストが重い/長期タスク | `prepare_for_new_conversation` → `write_memory`(handoff) |
| 関連情報の確認 | `list_memories` → `read_memory` |

## 6. Serena を使わない場合（明示が必要）

以下の場合のみ Serena 以外のツールを使用可能。**理由を短く明示すること**：

- ファイルが存在しない（新規作成で `create_text_file` が適さない場合）
- LSP がサポートしていない言語/ファイル形式（JSON, YAML, Markdown 等）
- バイナリファイル（画像、PDF 等）
- Serena ツールがエラーを返した場合

## Red Flags - STOP

以下の思考が浮かんだら **STOP**。Serena を使うべきサイン：

| 思考 | 現実 |
|------|------|
| 「全文読まないと分からない」 | `get_symbols_overview` を使え |
| 「grep で探す」 | `find_symbol` / `search_for_pattern` を先に |
| 「ファイル全体を書き換える」 | `replace_symbol_body` / `replace_content` を使え |
| 「手動で参照を追う」 | `find_referencing_symbols` を使え |
| 「Serena は面倒」 | Serena は高速かつ正確。面倒に感じるのは習熟不足 |

## 7. 出力フォーマット（簡潔）

- 何を Serena で確認したか（使ったツール種別）
- どのファイル/シンボルをどう変えたか（最小限）
- 変更点の要約（必要なら）

**コード全文の貼り付けは避け、要点と差分中心で説明する。**
