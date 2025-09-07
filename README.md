# 故障診断チャート・アプリケーション「アルバトロス」

オペレーターのスキルレベルに応じて、最適なUI/UXを提供する、次世代の故障診断チャートアプリケーションです。

---

## 🚀 アプリケーションURL

### 🌐 本番環境 (Production)
ユーザーが実際にアクセス・利用する環境です。

- **サイトURL:** [`https://albatross-2025.fly.dev/`](https://albatross-2025.fly.dev/)
- **管理サイトURL:** [`https://albatross-2025.fly.dev/admin/`](https://albatross-2025.fly.dev/admin/)

### 💻 ローカル開発環境 (Development)
開発・テストを行うための、個人のPC上の環境です。

- **サイトURL:** `http://127.0.0.1:8000/app/charts/`
- **管理サイトURL:** `http://127.0.0.1:8000/admin/`

---

## ✨ 主な機能

- **レベル別UI/UX:** 初級・中級・上級の3つのモードを搭載。
- **高精度ログ機能:** `yes/no/unknown`で、操作の有効性を正確に記録。
- **DB連動型コンテンツ:** 管理サイトから、チャートの内容をGUIで追加・編集可能。
- **ユーザー設定:** テーマカラーや文字サイズを、ユーザーごとに記憶。

## 🛠️ 使用技術

- **Backend:** Python, Django
- **Frontend:** JavaScript (Vanilla JS), Bootstrap 5
- **Database:** PostgreSQL (Production), SQLite (Development)
- **Deployment:** Fly.io, Docker
