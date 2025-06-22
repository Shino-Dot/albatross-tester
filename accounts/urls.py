from django.urls import path
from . import views  # viewsモジュールをインポート

app_name ="accounts"

# 5/12---includeを追加
# アカウントアプリにURLパイ引っ越し

urlpatterns = [
    path("login/", views.MyLoginView.as_view(), name="login"),
    path("logout/", views.MyLogoutView.as_view(), name="logout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("password_change/", views.MyPasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/", views.MyPasswordChangeDoneView.as_view(), name="password_change_done"),
    path("delete/", views.AccountDeleteView.as_view(), name="account_delete"),
    path('delete/complete/', views.AccountDeleteCompleteView.as_view(), name='account_delete_complete'),
]
# 後ほど新規登録などのURLも追加していく
# 5/14---サインアップパス追加
# ブラウザで /accounts/signup/ っていうURLにアクセスすると、さっき作った SignUpView が動いて、signup.html が表示されるようになる
# 5/19---削除処理対応のURL追記