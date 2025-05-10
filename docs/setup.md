# （事前準備）1dayインターン環境構築

# poetry関連

自分の環境にgitがない場合は各自インストールしておいてください。

## Linux, MacOS, WSL 環境向け

### pyenvのインストール

pyenvが既にインストールされている場合は 5. から進めてください。

1. GitHub からリポジトリを clone し、 `~/.pyenv` というパスでディレクトリを置く

```bash
$ git clone git@github.com:pyenv/pyenv.git ~/.pyenv
# https で GitHub に接続する場合
$ git clone https://github.com/pyenv/pyenv.git ~/.pyenv
```

(Option): 高速化するオプションを適用できる。失敗しても pyenv は正常に動作するので、とりあえず以下のコマンドを叩いておくと良い

```bash
$ cd ~/.pyenv && src/configure && make -C src && cd
```

1. [https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv) の各 shell の方法に従って設定を追加していく。基本的に手順通りにコマンドを叩けば良い。Bash の場合まず、  `$~/.bashrc` に次のようにして設定を追加する。

```bash
$ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
$ echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
$ echo 'eval "$(pyenv init -)"' >> ~/.bashrc
```

1. `~/.profile`, `~/.bash_profile`, `~/.bash_login` が存在する場合、そこに次のようにして設定を追加する。無ければ `~/.profile` を作成して、追加する。
    - (下記は `~/.profile` の場合なので、適宜 echo で流す先は変更すること)

```bash
$ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
$ echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
$ echo 'eval "$(pyenv init -)"' >> ~/.profile
```

1. shell をリセットして反映させる

```bash
$ exec $SHELL  # restart
$ pyenv --version  # check your pyenv command
```

### poetryのインストール

1.  以下のversionのpythonをインストール

```bash
$ pyenv install 3.10.11
$ pyenv global 3.10.11
```

1. pipxをインストール

```bash
$ pip install pipx
```

1. pipx で入れたツールを利用するために `PATH` に保存先を追加する (以下は `~/.bashrc` に設定を保存しておく場合)

```bash
$ echo 'export PATH=${HOME}/.local/bin:$PATH' >> ~/.bashrc
$ exec $SHELL
```

1. pipx でpoetryをインストール

```bash
$ pipx install poetry
```

※ kerying 周りでエラーが出ることがあるため、以下のコマンドを叩いておくことを推奨する (Bash の場合)

```bash
$ echo 'export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring' >> ~/.bashrc
$ exec $SHELL
```

1. poetryの仮想環境をプロジェクトディレクトリ以下に置くようにする

```bash
$ poetry config virtualenvs.in-project true
```

## Windows環境向け（Powershell）

### pyenvのインストール

pyenvが既にインストールされている場合は 5. から進めてください。

1. Githubからリポジトリをcloneし、`$HOME\.pyenv`というパスでディレクトリを置く

```powershell
> git clone git@github.com:pyenv/pyenv.git "$HOME\.pyenv"
# https で GitHub に接続する場合
> git clone https://github.com/pyenv-win/pyenv-win.git "$HOME\.pyenv"
```

1. 環境変数を設定

```powershell
> [System.Environment]::SetEnvironmentVariable('PYENV',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
> [System.Environment]::SetEnvironmentVariable('PYENV_ROOT',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
> [System.Environment]::SetEnvironmentVariable('PYENV_HOME',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
```

1. 環境変数パスを設定

```powershell
> [System.Environment]::SetEnvironmentVariable('PATH', $env:USERPROFILE + "\.pyenv\pyenv-win\bin;" + $env:USERPROFILE + "\.pyenv\pyenv-win\shims;" + [System.Environment]::GetEnvironmentVariable('PATH', "User"),"User")
```

1. powershellを再起動し、以下のコマンドを試す

```powershell
> pyenv --version
```

`スクリプトの実行が無効になっている`というエラーが出る場合、以下のコマンドを実行し、再度試してみてください

```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### poetry のインストール、初期設定

1. 以下のversionのpythonをインストール

```powershell
> pyenv install 3.10.11
> pyenv global 3.10.11 # global設定にしたくない方は、プロジェクトのディレクトリに移動後にpyenv localを実行
```

1. pipxをインストール

```powershell
> python -m pip install --user pipx
> python -m pipx ensurepath
```

1. poetryをインストール

```powershell
> python -m pipx poetry
```

1. poetryの仮想環境をプロジェクトディレクトリ以下に置くようにする

```powershell
> poetry config virtualenvs.in-project true
```

# VScode

今回はエディターとして、VSCodeを利用することを推奨します。拡張機能として以下をインストールしてください。

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
- [mypy](https://marketplace.visualstudio.com/items?itemName=ms-python.mypy-type-checker)

好きな場所で、1Dayインターン用のワークスペースを作成してください。

ワークスペースの直下で、VScodeの設定ファイル`.vscode/settings.json`を作成します。

```python
$ touch .vscode/settings.json  # Bash

> New-Item .vscode/settings.json  # Powershell
```

ファイルの中身を以下のようにします。

```powershell
{
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "python.analysis.autoImportCompletions": false,
    "python.analysis.diagnosticMode": "workspace",
    "python.analysis.typeCheckingMode": "off",
    // mypy
    "mypy-type-checker.importStrategy": "fromEnvironment",
    // test
    "python.testing.pytestEnabled": true,
    // ruff
    "ruff.lint.enable": true,
    "ruff.importStrategy": "fromEnvironment",
    // ruff formatter
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll": "explicit",
            "source.organizeImports": "explicit"
        },
        "editor.defaultFormatter": "charliermarsh.ruff",
    }
}
```

# 動かしてみる

## Poetry仮想環境の作成

引き続き、先ほど作成したワークスペース内で作業します。

poetry仮想環境を作成するために、pyproject.tomlを作成します。

```bash
$ touch pyproject.toml  # Bash

> New-Item pyproject.toml  # Powershell
```

中身には以下をコピーしてください。

```python
[tool.poetry]
name = "1-day-internship-app"
version = "0.1.0"
description = "1day intern app"
authors = ["Sansan, Inc."]
license = "Proprietary"

[tool.poetry.dependencies]
python = ">=3.10,<3.11"
streamlit = "1.33.0"
streamlit-agraph = "0.0.45"
requests = "^2.31.0"
types-requests = "^2.31.0.20240406"

[tool.poetry.group.dev.dependencies]
mypy = "^1.9.0"
pytest = "^8.1.1"
ruff = "^0.3.7"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.mypy]
check_untyped_defs = true
ignore_errors = false
strict_optional = true
warn_unused_configs = true
warn_unused_ignores = true
warn_redundant_casts = true
ignore_missing_imports = true

[tool.ruff]
target-version = "py310"
line-length = 120
select = ["ALL"]
ignore = [
    # missing-trailing-comma
    "COM812",
    # ambiguous-variable-name
    "E741",
    #  single-line-implicit-string-concatenation
    "ISC001",
    # assert
    "S101",
    # suspicious-non-cryptographic-random-usage
    "S311",
    # unnecessary-assign
    "RET504",
    # magic-value-comparison
    "PLR2004",
    # pydocstyle
    "D",
    # flake8-annotations
    "ANN",
]
exclude = [
    ".git",
    ".github",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
]

[tool.ruff.mccabe]
max-complexity = 5

```

`tool.poetry.dependencies`, `tool.poetry.group.dev.dependencies`にインストールしたいpythonライブラリとそのバージョンを記述します。

`tool.poetry.group.dev.dependencies` には、テスト関連のライブラリなど、開発環境にのみインストールしたいライブラリを記述します。オプションなしのpoetry installコマンドですべてのライブラリをインストールします。.venvフォルダにpoetry仮想環境が作成されます。仮想環境内でコマンドを実行したい場合は、poetry run を先頭に書くことで実行できます。

```bash
$ poetry install

$ poetry run python  # poetry仮想環境でpythonを起動
```

`tool.mypy`や`tool.ruff`はリンター、フォーマッターに関する設定を記述しています。リンター、フォーマッターに関してより深く知りたい方はこちら（あとで貼る）の記事を参考にしてください。

ライブラリを追加したい場合は

```python
$ poetry add (ライブラリ名)
```

を実行することで、ライブラリ間の依存関係を考慮しつつ、自動でインストールされます。ライブラリ名は[PyPI](https://pypi.org/)に載っているものと一致させる必要があります。その他、詳しく知りたい方は[公式ドキュメント](https://python-poetry.org/docs/pyproject/)を参照してください。

## Streamlitの実装

StreamlitはPythonでさくっとUIを作ることができるライブラリです。R&Dでは実際に [Sansan Labs](https://sin.sansan.com/best_practice/sansan-labs-2/) という実験的な機能を提供するサービスで使われています。その他にも Google X や Yelp、Uber などでも使われているようです（[参考](https://streamlit.io/)）。

Streamlitを実行するために、設定ファイル`config.toml`を作成します。

```bash
$ touch .streamlit/config.toml  # Bash

> New-Item .streamlit/config.toml  # Powershell
```

中身の設定値は以下のように設定してください。

```bash
[global]
developmentMode = false

[server]
port = 8080
runOnSave = false
headless = true

[browser]
gatherUsageStats = false
serverAddress = "localhost"

[client]
showErrorDetails = false
toolbarMode = "minimal"

[ui]
hideTopBar = true

[theme]
base="light"
primaryColor="#004E98"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F8F9FA"
textColor="#002060"
```

今回は設定について詳しく説明しませんが、気になる方は[公式ドキュメント](https://docs.streamlit.io/develop/api-reference/configuration/config.toml)を参照してください。

それでは、Streamlitでページを作成しましょう。サンプルとして、表データを描画するスクリプトを作ってみます。

pythonファイルを作成します。

```bash
$ touch display_table.py  # Bash

> New-Item display_table.py  # Powershell
```

中身は以下の通りです。

```python
from io import StringIO

import pandas as pd
import streamlit as st

# タイトル
st.title("表の描画")

# ダミーデータ。本番ではAPIから取得する。
data = """
user_id,company_id,full_name,company_name,address,phone_number
1562970695,346703132,山崎 舞,合同会社中村建設,和歌山県横浜市西区花島2丁目4番18号 箪笥町コート059,090-4299-5127
5062375141,7921731533,高橋 直子,佐藤情報有限会社,山形県日野市日本堤22丁目27番8号 浅草橋アーバン760,08-6736-3477
2145329705,5538492855,佐藤 零,岡本鉱業有限会社,兵庫県富里市勝どき15丁目4番11号 湯宮アーバン985,59-7844-0992
2421227868,3631070993,森 春香,松本農林合同会社,長崎県墨田区芝公園18丁目17番11号,36-3927-4883
1958145663,6213609077,佐々木 智也,佐藤印刷合同会社,神奈川県神津島村大中8丁目21番12号,080-9829-8733
8115335218,1911213317,小林 加奈,山本建設有限会社,佐賀県我孫子市西小来川33丁目22番7号,090-1939-2614
9349866916,8252429160,石川 舞,株式会社山田電気,北海道杉並区松石35丁目18番15号 長畑ハイツ620,080-9821-5323
3051876578,6524071334,森 聡太郎,西村保険合同会社,静岡県新島村箭坪20丁目7番17号,070-3139-2253
8757269752,7109725063,小林 加奈,山崎印刷合同会社,神奈川県板橋区轟30丁目1番20号 パレス蟇沼142,090-1886-0925
3087995951,4202933668,井上 太一,株式会社加藤運輸,北海道横浜市神奈川区四区町6丁目19番11号 氏家コーポ195,08-9498-6285
"""

df = pd.read_csv(StringIO(data))

st.dataframe(df)
```

ここで、実際に描画処理を記述している部分は、タイトル表示`st.title("表の描画")`と表の描画`st.dataframe(df)` の2行のみです。このように、streamlitでは直感的に素早くUIを作成することができます。

それでは、手元で実行してみましょう。

```bash
$ poetry run streamlit run display_table.py
```

`http://localhost:8080`に接続し、以下のような画面が出ると成功です。

![スクリーンショット 2024-05-17 12.07.45.png](%EF%BC%88%E4%BA%8B%E5%89%8D%E6%BA%96%E5%82%99%EF%BC%891day%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%B3%E7%92%B0%E5%A2%83%E6%A7%8B%E7%AF%89%2064891fd6cb214b858199cdabd6dcd3f9/%25E3%2582%25B9%25E3%2582%25AF%25E3%2583%25AA%25E3%2583%25BC%25E3%2583%25B3%25E3%2582%25B7%25E3%2583%25A7%25E3%2583%2583%25E3%2583%2588_2024-05-17_12.07.45.png)

## 便利なStreamlitツールの紹介

### Plotly

グラフや図を簡潔に描画できるライブラリ（[参考](https://plotly.com/python/)）。

以下のサンプルコードを実行し、UI上のボタンを押すと、折れ線グラフが描画されます。

```python
import random

import plotly.graph_objects as go
import streamlit as st

# タイトル
st.title("グラフの描画")

def display_plot(xx: list[int], yy: list[int]) -> None:
    fig = go.Figure()

    # データを追加する
    fig.add_trace(go.Scatter(x=xx, y=yy, mode="lines", name="New Trace"))

    # レイアウトを更新する
    fig.update_layout(title_text="Graph Example")

    st.plotly_chart(fig)

# 新しい作成し、描画するボタン
if st.button("グラフを作成"):
    # 新しいデータを作成する
    points_num = 10
    xx = list(range(points_num))
    yy = random.sample(range(10, 20), points_num)

    display_plot(xx, yy)
```

`if st.button()` 以下に、ボタンが押されたときの処理を書きます。

`graph_objectsのFigure()`でfigureが初期化されます。`fig.add_trace()`で描画したいグラフの情報を入力します。ここで複数のグラフを追加することもできます。`fig.update_layout`で図全体のレイアウトを設定（上書き）することができます。最後に、`st.plotly_chart(fig)`で仮面上にグラフが描画されます。

![スクリーンショット 2024-05-17 18.08.14.png](%EF%BC%88%E4%BA%8B%E5%89%8D%E6%BA%96%E5%82%99%EF%BC%891day%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%B3%E7%92%B0%E5%A2%83%E6%A7%8B%E7%AF%89%2064891fd6cb214b858199cdabd6dcd3f9/%25E3%2582%25B9%25E3%2582%25AF%25E3%2583%25AA%25E3%2583%25BC%25E3%2583%25B3%25E3%2582%25B7%25E3%2583%25A7%25E3%2583%2583%25E3%2583%2588_2024-05-17_18.08.14.png)

### streamlit_agraph

グラフ（ネットワーク）を描画できるライブラリ（[参考](https://github.com/ChrisDelClea/streamlit-agraph)）。

以下のサンプルコードを実行してみると、画面上にネットワークが表示されます。

```python
import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph

# タイトル
st.title("類似人物検索")

st.write(f"類似人物")

# 描画するNodeの登録
nodes = [
    Node(id="taro", label="taro", shape="circle"),
    Node(id="ichiro", label="ichiro", shape="circle"),
    Node(id="hanako", label="hanako", shape="circle"),
]

# 描画するEdgeの登録
edges = [
    Edge(source="taro", target="ichiro", label="0.9"),
    Edge(source="taro", target="hanako", label="0.8"),
]

# グラフの描画設定
config = Config(
    height=500,
    directed=False,
    physics=True,
)

# 描画
agraph(nodes, edges, config)

```

このように、ノードリスト(nodes)、エッジリスト(edges)、描画設定(config)を定義すれば簡単にネットワークを描画できます（[参考](https://github.com/ChrisDelClea/streamlit-agraph)）。

![スクリーンショット 2024-05-27 19.25.24.png](%EF%BC%88%E4%BA%8B%E5%89%8D%E6%BA%96%E5%82%99%EF%BC%891day%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%B3%E7%92%B0%E5%A2%83%E6%A7%8B%E7%AF%89%2064891fd6cb214b858199cdabd6dcd3f9/%25E3%2582%25B9%25E3%2582%25AF%25E3%2583%25AA%25E3%2583%25BC%25E3%2583%25B3%25E3%2582%25B7%25E3%2583%25A7%25E3%2583%2583%25E3%2583%2588_2024-05-27_19.25.24.png)
