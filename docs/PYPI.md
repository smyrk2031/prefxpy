# PrefxPy / PyPI への公開手順（Trusted Publishing 推奨）

このリポジトリ直下（`pyproject.toml` がある階層）で GitHub Actions と PyPI を連携します。

## 前提

- GitHub リポジトリがある（例: `https://github.com/smyrk2031/prefxpy`）。
- PyPI / TestPyPI で **Trusted Publisher** を登録できる。

## 手順（TestPyPI で試す）

1. [TestPyPI](https://test.pypi.org/manage/account/publishing/) で **Add a new pending publisher** を選ぶ。
2. **PyPI** のフォームで次を設定する（実際の名前に合わせて変更）。
   - Owner: GitHub のユーザーまたは Organization
   - Repository name: `prefxpy`
   - Workflow name: `publish.yml`
   - Environment name: 空欄（環境を使わない設定の場合）
3. GitHub で **Actions → Publish → Run workflow** を開き、`repository` を **testpypi** にして実行する。
4. アップロード確認:

   ```bash
   pip install --index-url https://test.pypi.org/simple/ prefxpy
   ```

## 手順（本番 PyPI）

1. [pypi.org](https://pypi.org/manage/account/publishing/) で同様に Trusted Publisher を登録する。
2. **Publish** ワークフローを **repository: pypi** で手動実行する、またはバージョンを上げてタグを押す:

   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

   `v*` タグが付いた push では、自動的に **本番 PyPI** へ公開するジョブが走る。

## バージョンとタグ

- `pyproject.toml` の `version` と Git タグを一致させる運用を推奨する。
- 先に `CHANGELOG.md` と `prefxpy/__init__.py` を揃えてからタグ付けする。

## メンテナ情報

- 実装や依存の変更がなければ、`docs/PYPI.md` を触らなくてよい。
- Trusted Publisher の Workflow 名やブランチを変えたときだけ、PyPI 側の設定を更新する。
