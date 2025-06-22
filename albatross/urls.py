from django.urls import path, include
from django.contrib import admin
from accounts import views as accounts_views

# from . import viewsでviews.py を読み込み
# テンプレートとかでURLを指定する時に {% url 'albatross_app:login' %} みたいに書けるようにするための設定(ショートカット的な)
# インクルード追加
# app_name = "albatross_app"左記削除
# ここは全体の管理のため上記の特定のアプリの名前は書かない、指定しない
# from accounts import views as accounts_views のインポート追記



urlpatterns = [
    path('admin/', admin.site.urls),
    # path("app/", include("albatross_app.urls")),
    path("accounts/", include("accounts.urls")),
    path("", accounts_views.MyLoginView.as_view(), name="top_login"),
    path("app/", include("albatross_app.urls", namespace="albatross_app")),
]
# path2行目のappはurlに表示される部分のためアンスコは入れずにスッキリさせる
# pathのあとの（）内で第一引数がURL表示部分、第二引数が「どのアプリの urls.py ファイルを読み込んでね！」っていう、Pythonモジュールへのパス
# 5/14---このパス("app/", include("albatross_app.urls")),は一時的にコメントアウト
# 上記はランサーバーでエラーになる原因と思われるため一時的にコメントアウト
# サイトのルート('/') にアクセスが来たら、accountsアプリのMyLoginViewを直接呼び出す！