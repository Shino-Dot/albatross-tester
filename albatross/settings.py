"""
Django settings for albatross project.
"""

from pathlib import Path
import os
import sys
from django.urls import reverse_lazy
import dj_database_url

# プロジェクトのベースディレクトリ
BASE_DIR = Path(__file__).resolve().parent.parent

# 【改善内容①】本番環境の判定をRender専用に整理
# 【改善理由】Fly.ioは削除済みのため、関連する環境変数チェックを除去。
#             判定条件をRenderのみに絞ることで意図が明確になる。
IS_PRODUCTION = "RENDER" in os.environ

# 【改善内容②】SECRET_KEYのハードコーディングを廃止
# 【改善理由】フォールバック値がコードに残ると、リポジトリ公開時に
#             セッション偽造やCSRF突破のリスクが生まれる。
#             本番では未設定時に即時終了、開発では警告用仮キーを使用。
_secret_key = os.environ.get("SECRET_KEY")
if not _secret_key:
    if IS_PRODUCTION:
        sys.exit("致命的エラー: 環境変数 SECRET_KEY が設定されていません。")
    else:
        _secret_key = "dev-only-insecure-key-do-not-use-in-production"

SECRET_KEY = _secret_key

# 本番／開発環境別の基本設定
if IS_PRODUCTION:
    DEBUG = False
    ALLOWED_HOSTS = ["*"]

    # CSRF設定（環境変数でデプロイ先URLを指定）
    CSRF_TRUSTED_ORIGINS_ENV = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
    if CSRF_TRUSTED_ORIGINS_ENV:
        CSRF_TRUSTED_ORIGINS = [CSRF_TRUSTED_ORIGINS_ENV]
    else:
        CSRF_TRUSTED_ORIGINS = []
else:
    DEBUG = True
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
    CSRF_TRUSTED_ORIGINS = []


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "accounts",
    "logs",
    "albatross_app",
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'albatross.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'albatross.wsgi.application'

# ==========================================================
# データベース設定
# ==========================================================
if IS_PRODUCTION:
    # 【改善内容③】DATABASE_URLのNullチェックを追加
    # 【改善理由】os.environ.get()はキーが未設定の場合Noneを返す。
    #             Noneに対して文字列操作を行うとTypeErrorが発生し
    #             サーバーが起動しない。明示的なガード節で
    #             エラーの原因を一目で特定できるようにする。
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        sys.exit("致命的エラー: 環境変数 DATABASE_URL が設定されていません。")

    if 'sslmode=disable' in database_url:
        database_url = database_url.replace('sslmode=disable', 'sslmode=require')

    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=600
        )
    }
else:
    # 開発環境はSQLite3を使用
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==========================================================
# パスワードバリデーション
# ==========================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==========================================================
# 国際化
# ==========================================================
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True

# ==========================================================
# 静的ファイル
# ==========================================================
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# 本番環境のみWhiteNoiseによる圧縮を有効化
if IS_PRODUCTION:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================================
# 認証関連のリダイレクト設定
# ==========================================================
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "albatross_app:chart_type_list"
LOGOUT_REDIRECT_URL = reverse_lazy("accounts:login")