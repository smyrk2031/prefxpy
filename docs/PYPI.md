# PrefxPy / PyPI 公開フロー

PrefxPy は GitHub Actions と PyPI の **Trusted Publishing** を使って公開します。
API token やパスワードを GitHub Secrets に置かず、PyPI 側で「この GitHub リポジトリのこの workflow からの公開を許可する」と登録する方式です。

この手順は次のリポジトリ構成を前提にしています。

- GitHub: `https://github.com/smyrk2031/prefxpy`
- Workflow: `.github/workflows/publish.yml`
- Package name: `prefxpy`
- Current version: `0.1.3`

## 全体像

```text
ローカルで変更
  ↓
version / CHANGELOG / __init__.py を更新
  ↓
GitHub に push
  ↓
CI が通る
  ↓
TestPyPI に手動公開して確認
  ↓
Git tag vX.Y.Z を push
  ↓
本番 PyPI に自動公開
```

## 1. 事前準備

### GitHub 側

GitHub リポジトリに次が入っていることを確認します。

- `pyproject.toml`
- `prefxpy/`
- `.github/workflows/ci.yml`
- `.github/workflows/publish.yml`

`publish.yml` は次の動きをします。

- 手動実行で `repository: testpypi` を選ぶと TestPyPI に公開する
- 手動実行で `repository: pypi` を選ぶと本番 PyPI に公開する
- `v*` タグを push すると本番 PyPI に公開する

普段の本番公開は **タグ push** を使います。手動の `pypi` 公開は、タグ運用に移る前の確認や復旧時だけ使う想定です。

### PyPI / TestPyPI 側

アカウントを作り、できれば 2FA を有効化します。

- TestPyPI: https://test.pypi.org/
- PyPI: https://pypi.org/

## 2. TestPyPI に Trusted Publisher を登録する

TestPyPI で先に試します。

1. https://test.pypi.org/manage/account/publishing/ を開く。
2. **Add a new pending publisher** を選ぶ。
3. 次の値を入力する。

| 項目 | 値 |
| --- | --- |
| PyPI Project Name | `prefxpy` |
| Owner | `smyrk2031` |
| Repository name | `prefxpy` |
| Workflow name | `publish.yml` |
| Environment name | 空欄 |

Environment name は、GitHub Actions の environment を使っていないため空欄にします。

## 3. TestPyPI に公開する

GitHub で次を開きます。

https://github.com/smyrk2031/prefxpy/actions/workflows/publish.yml

1. **Run workflow** を押す。
2. `repository` に `testpypi` を選ぶ。
3. **Run workflow** を押す。
4. workflow が緑になるまで待つ。

成功すると TestPyPI にページができます。

https://test.pypi.org/project/prefxpy/

## 4. TestPyPI からインストール確認する

別の仮想環境で確認します。

```bash
python -m venv .venv-test
.venv-test\Scripts\activate
python -m pip install --upgrade pip
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ prefxpy
prefxpy --help
```

`--extra-index-url https://pypi.org/simple/` を付ける理由は、`aiohttp` や `httpx` などの依存パッケージを本番 PyPI から取得するためです。
TestPyPI は依存パッケージが揃っていないことがあるため、TestPyPI だけを見る設定だと依存解決に失敗する場合があります。

## 5. 本番 PyPI に Trusted Publisher を登録する

TestPyPI で確認できたら、本番 PyPI でも同じ設定をします。

1. https://pypi.org/manage/account/publishing/ を開く。
2. **Add a new pending publisher** を選ぶ。
3. 次の値を入力する。

| 項目 | 値 |
| --- | --- |
| PyPI Project Name | `prefxpy` |
| Owner | `smyrk2031` |
| Repository name | `prefxpy` |
| Workflow name | `publish.yml` |
| Environment name | 空欄 |

この時点ではまだアップロードされません。
次に GitHub Actions から初回公開されたとき、PyPI 側の pending publisher が実際の project に紐づきます。

## 6. 本番 PyPI に初回公開する

現在のバージョンは `0.1.3` です。
`pyproject.toml` と `prefxpy/__init__.py` のバージョンが `0.1.3` になっていることを確認してからタグを作ります。

```bash
git status
git pull --ff-only
git tag v0.1.3
git push origin v0.1.3
```

`v0.1.3` タグが push されると、GitHub Actions の `Publish` workflow が走り、本番 PyPI に公開されます。

公開後、次を確認します。

```bash
python -m venv .venv-pypi
.venv-pypi\Scripts\activate
python -m pip install --upgrade pip
python -m pip install prefxpy
prefxpy --help
```

PyPI のページも確認します。

https://pypi.org/project/prefxpy/

## 7. 今後アップデートするときの流れ

PyPI は一度公開した同じバージョンを上書きできません。
修正を公開するたびに、必ずバージョンを上げます。

例: `0.1.3` から `0.1.4` に上げる場合。

### 7-1. 変更を実装する

通常どおりコード・テスト・ドキュメントを変更します。

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

### 7-2. バージョンを更新する

最低限、次の 3 か所を揃えます。

- `pyproject.toml` の `version`
- `prefxpy/__init__.py` の `__version__`
- `CHANGELOG.md`

例:

```text
pyproject.toml        version = "0.1.4"
prefxpy/__init__.py   __version__ = "0.1.4"
git tag               v0.1.4
```

### 7-3. GitHub に push する

```bash
git status
git add .
git commit -m "Release 0.1.4"
git push origin main
```

GitHub Actions の `CI` が通ることを確認します。

### 7-4. TestPyPI で確認する

GitHub Actions の `Publish` workflow を手動実行し、`repository: testpypi` を選びます。

確認用環境では、キャッシュや既存インストールの影響を避けるため、バージョンを指定してインストールします。

```bash
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ "prefxpy==0.1.4"
prefxpy --help
```

### 7-5. 本番 PyPI に公開する

TestPyPI で問題なければ、本番公開用のタグを push します。

```bash
git tag v0.1.4
git push origin v0.1.4
```

公開後に確認します。

```bash
python -m pip install --upgrade prefxpy
prefxpy --help
```

## 8. バージョン番号の決め方

基本は Semantic Versioning に寄せます。

| 種類 | 例 | 使う場面 |
| --- | --- | --- |
| Patch | `0.1.3` → `0.1.4` | バグ修正、README 修正、小さな改善 |
| Minor | `0.1.4` → `0.2.0` | オプション追加、機能追加 |
| Major | `0.2.0` → `1.0.0` | 互換性のない変更 |

`1.0.0` までは、仕様が固まりきっていない段階として `0.x.y` を使い続けて問題ありません。

## 9. よくある失敗と対処

### `Trusted publishing exchange failure`

PyPI / TestPyPI 側の Trusted Publisher 設定と GitHub Actions が一致していない可能性があります。

確認する項目:

- Owner が `smyrk2031` か
- Repository name が `prefxpy` か
- Workflow name が `publish.yml` か
- Environment name が空欄か
- GitHub Actions が fork ではなく本体リポジトリで動いているか

### `File already exists`

同じバージョンをすでに PyPI / TestPyPI に公開済みです。
PyPI は同じ version の再アップロードを許可しません。

対処:

1. バージョンを上げる。
2. `CHANGELOG.md` を更新する。
3. commit し直す。
4. 新しいタグで公開する。

### `No matching distribution found`

主な原因は次のどれかです。

- まだ公開 workflow が成功していない
- インストール先の Python が `requires-python` を満たしていない
- TestPyPI から確認しているのに `--extra-index-url https://pypi.org/simple/` を付けていない
- バージョン指定が間違っている

確認:

```bash
python --version
python -m pip --version
```

PrefxPy は `pyproject.toml` で `requires-python = ">=3.10"` を指定しています。

## 10. メンテナ用チェックリスト

リリース前:

- [ ] `pyproject.toml` の version を更新した
- [ ] `prefxpy/__init__.py` の `__version__` を更新した
- [ ] `CHANGELOG.md` を更新した
- [ ] `python -m pytest` が通った
- [ ] GitHub Actions の CI が通った
- [ ] TestPyPI に公開してインストール確認した

本番公開:

- [ ] PyPI の Trusted Publisher が登録済み
- [ ] `git tag vX.Y.Z` を作成した
- [ ] `git push origin vX.Y.Z` を実行した
- [ ] GitHub Actions の Publish が通った
- [ ] `pip install prefxpy` でインストール確認した
- [ ] https://pypi.org/project/prefxpy/ を確認した
