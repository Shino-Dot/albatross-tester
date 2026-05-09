# Albatross — Deployment Package

## アプリケーション概要

コールセンターのオペレーター向け、故障診断サポートツール。

Yes/No形式の選択式UIで、オペレーターが質問に答えるだけで解決策にたどり着ける設計。  
電話対応中でも迷わず使えることを最優先としている。

### 主な仕様

| 項目           | 内容                                                                     |
| :------------- | :----------------------------------------------------------------------- |
| 同時接続数     | 50人同時接続を想定                                                       |
| データ保存     | 診断セッションごとに質問・回答・結果をDBに記録                           |
| ログ確認       | Webアプリ内からログ一覧を確認可能                                        |
| コンテンツ管理 | Django管理画面からカテゴリ・質問・選択肢を管理                           |
| データ可搬性   | コンテンツはJSONファイルでエクスポート可能。DB移行時もデータを維持できる |

蓄積したログは後々の分析・マニュアル改善サイクルに活用できる構成。

故障診断チャート・プラットフォームのデプロイ用パッケージ。  
サーバー構築の練習・検証用途を想定したクリーンな状態のコードベース。

[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)

---

## このリポジトリについて

特定のデプロイ先（PaaS等）に依存しない、汎用的なデプロイパッケージです。  
`.env` に環境変数を設定するだけで、任意のサーバー・コンテナ環境で動作します。

---

## 必要な環境

- Docker / Docker Compose
- PostgreSQL 14以上

---

## 環境構築手順

### 1. クローン

```bash
git clone https://github.com/amamiya-works/albatross-tester.git
cd albatross-tester
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を開き、以下の3項目を設定する。

| 変数名                 | 内容                                                  |
| :--------------------- | :---------------------------------------------------- |
| `SECRET_KEY`           | Djangoのシークレットキー（任意の強力な文字列）        |
| `DATABASE_URL`         | PostgreSQL接続URL                                     |
| `CSRF_TRUSTED_ORIGINS` | デプロイ先のURL（例: `https://your-app.example.com`） |

### 3. ビルド・起動

```bash
docker compose up --build
```

### 4. テーブル作成

```bash
docker compose exec web python manage.py migrate
```

### 5. データ投入

```bash
docker compose exec web python manage.py loaddata albatross_app/fixtures/initial_data.json
```

### 6. 管理者アカウント作成

```bash
docker compose exec web python manage.py createsuperuser
```

---

## 動作確認

ブラウザで `http://localhost:8000` にアクセスして起動を確認する。  
管理画面は `http://localhost:8000/admin` から利用可能。

---

## ファイル構成

```
albatross-tester/
├── accounts/                  # アカウント管理アプリ
├── albatross/                 # Djangoプロジェクト設定
├── albatross_app/             # メインアプリ
│   └── fixtures/
│       └── initial_data.json  # 初期データ（loaddata で投入）
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
├── runtime.txt
└── .env.example
```

---

## 本番運用時の注意

- `DEBUG=False` にする（`settings.py` の `IS_PRODUCTION` は環境変数 `RENDER` で制御）
- `CSRF_TRUSTED_ORIGINS` に本番URLを必ず設定する
- `SECRET_KEY` は十分な長さのランダム文字列を使用する
