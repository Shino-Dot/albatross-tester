from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt


# 5/13---reverse_lazy、generic、UserCreationForm、追加
# 5/17---PasswordChangeViewとPasswordChangeForm追加
# 5/19---AuthenticationFormとauthenticateとView追記、アカウント削除用
# 5/21---redirectとsettingsインポート追記
# 5/21---import logout追加
# 5/26---LoginView追記
# 6/21---CSRF追加


# 新規登録
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("accounts:login")
    # success_url = "/accounts/login/"
    template_name = "accounts/signup.html"

# 上記は上から使うフォームの指定、登録成功したらログインページに飛ばす、表示するHTMLテンプレートを指定。

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # ユーザーがログイン認証済みの場合
            # settings.LOGIN_REDIRECT_URL にリダイレクトする
            # LOGIN_REDIRECT_URL が設定されていなければ、サイトのルート ('/') にリダイレクト
            # (もし LOGIN_REDIRECT_URL が未設定で、ルートがログインページの場合、
            #  別の適切なログイン後ページURLを直接指定するのもアリ)    
            redirect_url = getattr(settings, "LOGIN_REDIRECT_URL", "/")
            if redirect_url == "/" and not request.user.has_perm(" some_permission_that_indicates_logged_in_area"):
                # 例: ルートがログインページで、まだチャート選択画面のURLが決まってない場合など、
                #     とりあえず '/admin/' など、確実に存在する場所に飛ばすのも手
                # redirect_url = '/admin/' # (これはあくまで例！)
                # もしくは、albatross_app のトップページのURL名を指定する (例: 'albatross_app:chart_list')
                pass # ここはマサ君のアプリの構成に合わせて調整してね！★チャート画面に飛ばす処理をあとで書く。
            
            return redirect(redirect_url)
        # ユーザーがログイン認証されていなければ、通常の新規登録処理を続行
        return super().dispatch(request, *args, **kwargs)

"""
上記に入る可能性のあるコード
        try:
            redirect_url = reverse_lazy('albatross_app:chart_top') # チャートのトップ画面へ
        except NoReverseMatch: # もし 'albatross_app:chart_top' がまだ無かったらフォールバック
            redirect_url = getattr(settings, 'LOGIN_REDIRECT_URL', '/')
        return redirect(redirect_url)
"""


# ログイン処理
# 5/13---下記accounts/login.htmlのアカウント部分を_appからアカウントに修正
# 5/14---スペルミス修正

class MyLoginView(LoginView):
    template_name = "accounts/login.html"
    # success_url は settings.LOGIN_REDIRECT_URL が使われる

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # 既にログイン済みの場合は、LOGIN_REDIRECT_URL にリダイレクト
            return redirect(settings.LOGIN_REDIRECT_URL or "/")# or '/' は念のため
        return super().dispatch(request, *args, **kwargs)



# ログアウト処理
class MyLogoutView(auth_views.LogoutView):
    pass
# ログアウト後のリダイレクト先は settings.py の LOGOUT_REDIRECT_URL で指定するのがおすすめ
# (例: LOGOUT_REDIRECT_URL = '/login/')


# パスワード変更（更新）処理
class MyPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change_form.html"
    success_url = reverse_lazy("accounts:password_change_done")

# MyPasswordChangeView っていう名前で、さっきインポートした PasswordChangeView をカッコ () の中に書いて「継承」してる。
# PasswordChangeView が持ってる便利な機能（パスワード変更処理とか、フォームの取り扱いとか）を、MyPasswordChangeView も使えるようになる


# パスワード変更完了のためのページの処理
class MyPasswordChangeDoneView(generic.TemplateView):
    template_name = "accounts/password_change_done.html"


# 5/19---削除系追記していく
# アカウント削除ビュー

@method_decorator(login_required, name="dispatch")
class AccountDeleteView(View):
    template_name = "accounts/account_delete_form.html"
    # success_url = reverse_lazy("accounts:login")
    # 削除再工事のリダイレクト先（今回はJSで制御かも）

    def get(self, request,*args, **kwargs):
        # GETリクエスト時 (最初にページを開いた時)
        # 空の認証フォームをテンプレートに渡す (パスワード入力欄のため)
        print("★★★ AccountDeleteView GET method CALLED! ★★★") # ← まずこれが呼ばれるか？
        print(f"★★★ User authenticated in GET: {request.user.is_authenticated} ★★★") # ← ログイン状態は？
        print(f"★★★ Session user_deleted_flag in GET: {request.session.get('user_deleted_and_needs_logout_flag')} ★★★") # ← セッションフラグは？
        print(f"★★★ Session show_modal_flag in GET: {request.session.get('show_delete_modal_on_load_flag')} ★★★") # ← セッションフラグは？

        form = AuthenticationForm()
        show_deleted_message_and_logout = request.session.pop('user_deleted_and_needs_logout_flag', False)
        # セッションから「モーダル自動表示」フラグを取得 (もしパスワード認証成功直後なら)
        show_modal_on_load = request.session.pop('show_delete_modal_on_load_flag', False)
        context = {
            "form": form,
            # "user_deleted_and_needs_logout": show_deleted_message_and_logout,
            "show_delete_modal_on_load": show_modal_on_load, # モーダル表示用フラグも渡す
        }
        print(f"★★★ GET時 context: {context}") # デバッグログ
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        context = {}
        print("--- ★1. AccountDeleteViewのPOSTメソッドが呼ばれました ---") # ★デバッグログ
        # POSTリクエスト時 (ユーザーがフォームを送信した時)
        # ここでパスワード認証と、最終確認後の削除処理を行う
        if "execute_delete" in request.POST and request.POST.get("execute_delete") == "true":
            print("--- ★2. execute_deleteリクエストを処理します ---") # ★デバッグログ
            # 最終確認後の実行フェーズ
            user_to_delete = request.user

            if user_to_delete.is_authenticated: # 念のためログインしてるか確認
                user_to_delete.is_active = False
                user_to_delete.save()
                # logout(request) # ここでログアウトしちゃう！
                
                print(f"--- ★3. ユーザー {user_to_delete.username} の is_active を False にしました ---") # ★デバッグログ★
                request.session['account_successfully_deleted_flag'] = True # 新しいセッションフラグ名
                print("--- ★4. 削除完了フラグをセッションにセットしました ---") # ★デバッグログ★
                return redirect('accounts:account_delete_complete') # ← 同じページにリダイレクトして、GETでフラグを読み込む
            else:
                print("★★★ 削除実行フェーズ: ユーザーが認証されていません (通常ありえない)")
                # 何らかのエラー処理 (ログインページへリダイレクトなど)
                return redirect('accounts:login')


        else:
            print(">>> パスワード認証フェーズ")
            # パスワード認証フェーズ
            form_data = request.POST.copy()
            form_data["username"] = request.user.username
            form = AuthenticationForm(request, data=form_data)


        if form.is_valid():
            # パスワード認証OK！
            print("★★★ パスワード認証成功！ ★★★") # デバッグ用
            # ここで、JavaScriptに「認証OKだよ」って伝えるか、
            # もしくは、特定のフラグを立てて再度同じテンプレートを表示し、
            # テンプレート側でJavaScriptのconfirmを出す、みたいな流れになるかな。
            request.session['show_delete_modal_on_load_flag'] = True
            return redirect('accounts:account_delete') # 同じページにリダイレクトしてGETでモーダル表示
        else:
                print("★★★ パスワード認証失敗… ★★★")
                context["form"] = form # エラーメッセージ付きのフォーム
                # ↓↓↓ ★変更点５：エラー時も context をちゃんと渡してrender ★↓↓↓
                return render(request, self.template_name, context)

            # 今回は、まず「パスワード認証が通った」ということを確認したいので、
            # 一旦、コンソールにメッセージを出すだけにしてみようか！

            # TODO: ここに最終確認ポップアップ表示のトリガーと、実際の削除処理を書く！
            # (Ajax使うか、もう一度POSTさせるか、など設計による)

            # 仮に、認証成功したら、メッセージ付きで同じページを再表示する例
            # (実際には、ここでJSを動かすための工夫が必要になる)

@method_decorator(csrf_exempt, name='dispatch')
class AccountDeleteCompleteView(View): # ← ★★★ このクラスがちゃんと存在してるか？ ★★★
    template_name = "accounts/account_delete_complete.html"

    def get(self, request, *args, **kwargs):
        print("★★★ AccountDeleteCompleteView GET method CALLED! ★★★")
        account_successfully_deleted = request.session.pop('account_successfully_deleted_flag', False)
        if not account_successfully_deleted:
            print(">>> 削除完了フラグなしでアクセスされました。リダイレクトします。")
            return redirect('accounts:login')

        context = {
            'user_deleted_and_needs_logout': True,
        }
        print(f"★★★ 削除完了ページ表示: context = {context}")
        return render(request, self.template_name, context)