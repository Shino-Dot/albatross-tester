import logging

from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic, View

logger = logging.getLogger(__name__)


# ==========================================================
# 新規登録
# ==========================================================
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("accounts:login")
    template_name = "accounts/signup.html"

    def dispatch(self, request, *args, **kwargs):
        # ログイン済みの場合はチャート選択画面へリダイレクト
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL or "/")
        return super().dispatch(request, *args, **kwargs)


# ==========================================================
# ログイン
# ==========================================================
class MyLoginView(LoginView):
    template_name = "accounts/login.html"

    def dispatch(self, request, *args, **kwargs):
        # ログイン済みの場合はチャート選択画面へリダイレクト
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL or "/")
        return super().dispatch(request, *args, **kwargs)


# ==========================================================
# ログアウト
# ==========================================================
class MyLogoutView(auth_views.LogoutView):
    pass


# ==========================================================
# パスワード変更
# ==========================================================
class MyPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change_form.html"
    success_url = reverse_lazy("accounts:password_change_done")


class MyPasswordChangeDoneView(generic.TemplateView):
    template_name = "accounts/password_change_done.html"


# ==========================================================
# アカウント削除
# ==========================================================
@method_decorator(login_required, name="dispatch")
class AccountDeleteView(View):
    template_name = "accounts/account_delete_form.html"

    def get(self, request, *args, **kwargs):
        # パスワード認証成功後のモーダル表示フラグを取得
        show_modal_on_load = request.session.pop('show_delete_modal_on_load_flag', False)
        context = {
            "form": AuthenticationForm(),
            "show_delete_modal_on_load": show_modal_on_load,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # 削除実行フェーズ（モーダルで「はい」を押した後）
        if "execute_delete" in request.POST and request.POST.get("execute_delete") == "true":
            if request.user.is_authenticated:
                request.user.is_active = False
                request.user.save()
                request.session['account_successfully_deleted_flag'] = True
                return redirect('accounts:account_delete_complete')
            return redirect('accounts:login')

        # パスワード認証フェーズ
        form_data = request.POST.copy()
        form_data["username"] = request.user.username
        form = AuthenticationForm(request, data=form_data)

        if form.is_valid():
            # 認証成功：モーダル表示フラグを立ててリダイレクト
            request.session['show_delete_modal_on_load_flag'] = True
            return redirect('accounts:account_delete')

        # 認証失敗：エラーメッセージ付きフォームを再表示
        return render(request, self.template_name, {"form": form})


# ==========================================================
# アカウント削除完了
# ==========================================================
class AccountDeleteCompleteView(View):
    template_name = "accounts/account_delete_complete.html"

    def get(self, request, *args, **kwargs):
        # 【改善内容】削除完了フラグがない場合はログインページへ
        # 【改善理由】URLを直打ちされた場合でも正規フロー以外のアクセスを弾く
        account_successfully_deleted = request.session.pop(
            'account_successfully_deleted_flag', False
        )
        if not account_successfully_deleted:
            return redirect('accounts:login')

        # 【改善内容】削除完了後に即座にログアウト
        # 【改善理由】is_activeをFalseにしただけではセッションが残り、
        #             削除済みユーザーとして操作が継続できてしまうため
        logout(request)

        return render(request, self.template_name, {'user_deleted_and_needs_logout': True})