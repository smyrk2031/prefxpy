# Changelog

## 0.1.3

- ライセンス表記を整備（`THIRD_PARTY_NOTICES.md` 追加、README からリンク）。
- PyPI 配布物（sdist / wheel）に `LICENSE` と `THIRD_PARTY_NOTICES.md` を同梱。

## 0.1.2

- CLI コマンド名を `prefxpy` に統一（パッケージ名と一致）。
- `--target` 未指定時は `http://127.0.0.1:8000` を既定値に（`prefxpy` のみで起動可能）。
- 起動時に Public URL・注意点を表示。
- `/` は案内ページ、`/myapp/` 以外は分かりやすい 404 メッセージを返す。

## 0.1.1

- `prefxpy.toml` を `--config` で読み込めるようにした（CLI の指定はファイルより優先）。
- 設定の `[headers]` を上流リクエストへ付与（`X-Forwarded-*` は常に上書きで正規値を優先）。
- CI（pytest / 複数 Python）と PyPI／TestPyPI 公開用ワークフローを追加。

## 0.1.0

- 初期実装を追加。
- HTTP リバースプロキシ、prefix 配下公開、Forwarded ヘッダ付与を実装。
- pytest ベースの初期テストを追加。
