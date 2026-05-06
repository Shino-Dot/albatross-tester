# Albatross

故障診断チャート・プラットフォーム  
オペレーターの習熟度に応じて診断UIを動的に切り替える、カスタマーサポート向けWebアプリケーション。

[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-Vanilla-F7DF1E?style=for-the-badge&logo=javascript)](https://developer.mozilla.org/ja/docs/Web/JavaScript)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render)](https://render.com/)

**Live Demo:** https://albatross-w6pr.onrender.com

| ロール       | ユーザー名 | パスワード |
| :----------- | :--------- | :--------- |
| デモユーザー | demo       | demo1234   |

---

## 概要

紙マニュアルや静的フローチャートの運用課題として、
「初学者が途中で迷子になる」「習熟者には冗長すぎて非効率」という相反する問題がある。

Albatross はこの課題に対して、同一の診断ロジックから
**初級・中級・上級の3種類のUIをリアルタイムで切り替えて提供する**アプローチで解決を図った。

---

## 主要機能

### レベル別アダプティブUI

同一の診断データから、3段階のUIをレンダリングする。

- **初級:** ステップごとに丁寧な説明と選択肢を提示
- **中級:** 要点のみを表示し、操作ステップを圧縮
- **上級:** 全ステップをタイル表示。任意の順序で診断を進められる自由選択フロー。
  信号機コンセプト（赤・黄・青）でリスクを色分け表示し、タイムスタンプを自動記録。

### 診断ログ

全診断プロセスをセッション単位でログ化。「解決 / 未解決 / 途中終了」のステータスと
各ステップの操作履歴を記録し、期間・ステータスでの検索・ソートに対応。
ログデータはマニュアル自体の改善サイクルに活用できる構成としている。

### アクセシビリティ設定

4段階の文字サイズ変更と5種のカラーテーマを `localStorage` で永続化。
長時間業務での疲労軽減を考慮したUX設計。

### アカウント管理

二段階の退会フロー（認証 → 確認）と論理削除によるデータ整合性の保護を実装。

---

## 技術スタック

| 区分     | 技術                     | 選定理由                                   |
| :------- | :----------------------- | :----------------------------------------- |
| Backend  | Django 4.2 (Python)      | ORM と Admin による診断データの保守性      |
| Database | PostgreSQL               | 商用グレードの信頼性                       |
| Frontend | Vanilla JS / Bootstrap 5 | フレームワーク依存を排除した軽量動作       |
| Storage  | WhiteNoise               | 本番環境での静的ファイル配信の簡略化       |
| Infra    | Render / Docker          | コンテナ化による開発・本番環境の差異を排除 |

---

## 技術的な課題と解決

### 多階層データモデルの設計

チャート種別・ステップ・セッションログという3層のリレーションにおいて、
クエリパフォーマンスを維持するモデル構成を設計した。
`select_related` と `prefetch_related` の使い分けによるN+1問題への対処を含む。

### デプロイ時の SSL 接続エラー

PostgreSQL 接続時に `SSL SYSCALL error` が発生。
ログ解析の結果、自動生成される `DATABASE_URL` のパラメータと
Django の `OPTIONS` 設定の競合が原因と特定。
`settings.py` 内でURL文字列を動的にパースし、SSL設定を上書きするロジックを実装して解決。

### Fetch API と CSRF 対策

フォーム外からの非同期送信において、DjangoのCSRFミドルウェアと整合するよう、
Cookie からトークンを取得しリクエストヘッダに付与する実装を行った。

---

## コード品質の改善

本番運用前にコードレビューを実施し、以下の問題を特定・修正した。

**セキュリティ修正**

| 対象                | 修正内容                                                                                      |
| :------------------ | :-------------------------------------------------------------------------------------------- |
| `settings.py`       | `SECRET_KEY` のハードコーディングを廃止。本番環境では環境変数未設定時に即時終了する設計に変更 |
| `settings.py`       | `IS_PRODUCTION` の二重定義を解消                                                              |
| `accounts/views.py` | `csrf_exempt` の誤適用（本来不要な箇所への適用）を削除                                        |
| `accounts/views.py` | `print()` によるユーザー情報のログ出力を全削除                                                |
| `accounts/views.py` | `login_required` の適用漏れを修正                                                             |

**コード整理**

| 対象                | 修正内容                                         |
| :------------------ | :----------------------------------------------- |
| `accounts/views.py` | 不要なimport・未使用コメントの整理               |
| `log_list.html`     | HTMLタグのタイポ修正（`</slabel>` → `</label>`） |
| `help_filter.css`   | `display` / `opacity` の競合を解消               |
| `help_filter.css`   | 未定義CSS変数 `--border-color` を実値に置き換え  |

---

## AI活用について

設計・開発フェーズで LLM（主に Claude）を以下の用途で使用した。

| 用途           | 具体的な内容                                             |
| :------------- | :------------------------------------------------------- |
| 設計レビュー   | 多階層モデルのリレーション設計における複数案の比較検討   |
| コードレビュー | セキュリティ問題・未使用コードの洗い出しと修正方針の確認 |
| デバッグ補助   | SSL接続エラーの原因仮説の列挙と絞り込み                  |
| 実装調査       | Fetch API + Django CSRF 対策の実装パターンの整理         |

コードの自動生成には使用していない。
意思決定の高速化と見落としの防止が主な活用目的。
実装・デバッグ・本番確認はすべて自分で実施している。

---

## ローカル起動

```bash
git clone https://github.com/amamiya-works/albatross.git
cd albatross
cp .env.example .env   # 環境変数を設定
docker compose up --build
```
