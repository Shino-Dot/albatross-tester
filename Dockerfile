# --- 1. ベースとなるOSとPythonの環境を準備 ---
# Python 3.11 の、スリムなバージョンのOSを土台にします
FROM python:3.11-slim

# --- ★★★ ここからが、超重要！ ★★★ ---
# psycopg2が、正しくインストールされるために必要な、OSのツールを、先にインストールする！
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# --- ★★★ ここまでが、超重要！ ★★★ ---

# --- 2. 環境変数を設定 ---
# Pythonが、pycファイルとかを作らないようにするおまじない
ENV PYTHONDONTWRITEBYTECODE 1
# Pythonのログが、ちゃんと表示されるようにするおまじない
ENV PYTHONUNBUFFERED 1

# --- 3. 作業ディレクトリを作成＆移動 ---
# コンテナの中に、/app という名前のフォルダを作って、そこをメインの作業場所にする
WORKDIR /app

# --- 4. 必要なライブラリをインストール ---
# まず、ライブラリの一覧表(requirements.txt)だけを先にコピーする
COPY requirements.txt /app/
# requirements.txtに書かれてるライブラリを、全部インストールする
RUN pip install --no-cache-dir -r requirements.txt

# --- 5. プロジェクトの全ファイルをコピー ---
# ローカルの、このプロジェクトのファイルを、全部コンテナの/appフォルダにコピーする
COPY . /app/

# --- ▼▼▼ 6. 起動スクリプトをコピーして、実行権限を与える！ ▼▼▼ ---
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# --- 6. アプリを起動するコマンドを設定 ---
# このコンテナが起動した時に、このコマンドを実行してね！っていう命令
# Gunicornという本番用のWebサーバーを使って、albatrossプロジェクトを動かす
CMD ["/app/entrypoint.sh"]