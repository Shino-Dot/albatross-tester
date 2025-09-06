from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
# method_decorator をインポート！(クラスベースビューに@login_requiredを適用するため)
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from .models import ChartType
from django.shortcuts import render, get_object_or_404  # get_object_or_404 をインポート！
# ChartStep もインポート！
from .models import ChartType, ChartStep, TroubleshootingSession, SessionLog
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
import collections
from datetime import date, timedelta, datetime
from django.utils import timezone
from django.db.models import Case, When 

# 5/26---method_decoratorとListViewとChartType追加
# 5/26---仮ページはコメントアウト
# 5/27---JsonResponse とrequire_POSTと jsonインポート！
# 5/28---TroubleshootingSession, SessionLog 追加
# 6/12---インポートコレクションズ
# 6/22---tタイムデルタ、タイムゾーン追加
"""
@login_required
def some_test_view(request):
    return HttpResponse("ここは仮ぺです(ログイン必須)")
"""


@method_decorator(login_required, name="dispatch")  # クラスベースビュー全体をログイン必須にする
class ChartTypeListView(ListView):
    model = ChartType
    template_name = "albatross_app/chart_type_list.html"

    # (任意) もし、リストの並び順とかを細かく制御したい場合は、queryset をオーバーライド
    # def get_queryset(self):
    #     return ChartType.objects.order_by('name') # 例: 名前順に並べる

    # ▼▼▼ get_context_dataメソッドを、自分で定義する！ ▼▼▼
    def get_context_data(self, **kwargs):
        # まず、親クラスのメソッドを呼び出して、基本的なコンテキストを取得
        context = super().get_context_data(**kwargs)
        
        # DBから、全てのChartTypeを取得する
        all_chart_types = ChartType.objects.all().order_by('name') # 名前順に並べとくとキレイ

        # カテゴリごとにグループ分けするための、空の辞書を準備
        grouped_charts = collections.defaultdict(list)

        # 全てのチャートタイプをループして、カテゴリごとに仕分けしていく
        for chart_type in all_chart_types:
            # get_category_display() を使うと、'power'じゃなくて'電源'が取れる！
            category_display_name = chart_type.get_category_display()
            grouped_charts[category_display_name].append(chart_type)
        
        # 仕分けが終わった辞書を、テンプレートに渡す
        context['grouped_chart_types'] = dict(grouped_charts)
        
        return context
    # ▲▲▲ ここまでが、新しいメソッド！ ▲▲▲

@login_required  # もちろんログイン必須！
def start_chart_view(request, chart_type_id):  # URLから chart_type_id を受け取る
    # 指定されたIDの ChartType を取得 (もし存在しなかったら404エラー)
    chart_type = get_object_or_404(ChartType, pk=chart_type_id)

    # その ChartType に関連する全ての ChartStep を取得
    # (例: is_starting_step が True のものから順に、とか、もっと賢い取得方法も考えられるけど、
    #  まずは全部取ってきて、表示の制御はJSでやる方針なので、これでOK！)

    # ▼▼▼ 下の新しいロジックに、まるっと置き換わる！ ▼▼▼
    # --- 初級/中級用のデータを準備 ---
    chart_steps = ChartStep.objects.filter(chart_type=chart_type).order_by("id")
    starting_step = chart_steps.filter(is_starting_step=True).first()
    starting_step_id_for_js = starting_step.id if starting_step else None

    # --- 上級用のデータを準備 ---
    all_advanced_steps = ChartStep.objects.filter(chart_type=chart_type)
    final_steps = all_advanced_steps.filter(is_final_step=True).order_by('id')
    normal_steps = all_advanced_steps.filter(is_final_step=False)
    
    from django.db.models import Case, When
    normal_steps_query = normal_steps.order_by(
        Case(
            When(risk_level="low", then=1),
            When(risk_level="medium", then=2),
            When(risk_level="high", then=3),
            default=4
        ),
        "display_order") # さっきと同じ並び替えロジック

    grouped_steps = collections.defaultdict(list)
    for step in normal_steps_query:
        risk_label = step.get_risk_level_display()
        grouped_steps[risk_label].append(step)
    # ▲▲▲ ここまでが、新しいロジック！ ▲▲▲
    context = {
        "chart_type": chart_type,
        "chart_steps": chart_steps,
        "starting_step_id_for_js": starting_step_id_for_js,
        "grouped_steps_for_advanced": dict(grouped_steps), # ★★★ 上級UI用の新しいデータを追加！ ★★★
        "final_steps_for_advanced": final_steps,
    }
    return render(request, "albatross_app/chart_display.html", context)


# 5/26---"starting_step_id_for_js": starting_step_id_for_js,追加

@login_required  # ログイン必須にする
@require_POST  # POSTリクエストのみ受け付けるようにする
def save_chart_log_view(request):
    # if request.method == "POST":　# ← @require_POST を使ってるなら、このif文は無くてもOK！
    try:
        # リクエストのボディからJSONデータを読み込む
        data = json.loads(request.body)
        chart_type_id = data.get("chart_type_id")
        answers = data.get("answers")  # これが userAnswers オブジェクト

        # --- ▼▼▼ 新しいデータを受け取る！ ▼▼▼ ---
        is_resolved = data.get("is_resolved", True) # デフォルトはTrue (改善)
        resolved_step_id = data.get("resolved_step_id") # なければNoneになる
        # --- ▲▲▲ ここまで！ ▲▲▲

        # とりあえずコンソールに出力して確認！
        print("--- save_chart_log_view が呼ばれました！ ---")
        print(f"Chart Type ID: {chart_type_id}")
        print(f"Type of Chart Type ID: {type(chart_type_id)}")  # 型も見てみよう！
        print(f"Answers: {answers}")  # 辞書型になってるはず

        # TODO: ここで実際にデータベースに保存する処理を書く (次のフェーズ)
        if chart_type_id is None:
            # chart_type_id が None の場合はエラーレスポンス
            return JsonResponse({"status": "error", "message": "チャート種別がありません。 "}, status=400)
        
        chart_type_obj = get_object_or_404(ChartType, id=int(chart_type_id))

        # --- ▼▼▼ TroubleshootingSession を作る時に、新しいデータを追加！ ▼▼▼ ---
        resolved_step_obj = None # まずはNoneで初期化
        if resolved_step_id:
            try:
                # resolved_step_id があれば、ChartStepオブジェクトを取得
                resolved_step_obj = ChartStep.objects.get(id=int(resolved_step_id))
            except (ChartStep.DoesNotExist, ValueError):
                # 見つからなくても、まあエラーにはしないでおく
                resolved_step_obj = None

        # 2. TroubleshootingSession オブジェクトを作成して保存
        # (これは @login_required があるので request.user は必ず存在するはず)
        session = TroubleshootingSession.objects.create(
            user=request.user,
            chart_type=chart_type_obj,
            is_resolved=is_resolved,          # ★追加！
            resolved_step=resolved_step_obj  # ★追加！
            #  end_time はデフォルトで設定される
        )
        # session.save() # .create() を使った場合は、この .save() は不要

        # 3. answers をループして SessionLog オブジェクトを作成して保存
        if not isinstance(answers, dict):
            # answers が辞書型じゃない場合はエラー
            print(f"Answers が辞書型ではありません: {answers}")
            return JsonResponse({"status": "error", "message": "回答データが不正な形式です。"}, status=400)

        logs_created_count = 0
        for step_id_str, answer_value in answers.items():
            try:
                # ★★★ step_id も文字列で送られてくるので、intに変換 ★★★
                step_id_int = int(step_id_str)
                chart_step_obj = ChartStep.objects.get(id=step_id_int)

                # answer_value が None の場合は "unknown" にする
                user_answer = answer_value if answer_value is not None else "unknown"

                # answer が choices に含まれる値かチェック (より丁寧にするなら)
                valid_answers = [choice[0] for choice in SessionLog._meta.get_field("answer").choices]
                if user_answer not in valid_answers:
                    print(f"不正な回答です: step_id={step_id_int}, answer={user_answer}")
                    # ここでエラーにするか、'unknown'として記録を続けるか選べる
                    # 今回は 'unknown' にしちゃう例
                    user_answer = "unknown"

                SessionLog.objects.create(
                    session=session,
                    chart_step=chart_step_obj,
                    answer=user_answer
                )
                logs_created_count += 1
            except (ChartStep.DoesNotExist, ValueError):
                continue
        
        print(f"{logs_created_count} 件のセッションログを作成しました。")
        return JsonResponse({"status": "success", "message": f"結果を記録しました。（{logs_created_count}件のログ）"})

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "無効なJSONデータです。"}, status=400)
    except Exception as e:
        print(f"予期せぬエラーが発生しました：{e}")
        return JsonResponse({"status": "error", "message": "サーバー内部エラーが発生しました。"}, status=500)

    except json.JSONDecodeError:
        print("JSONデコードエラーが発生しました。")
        return JsonResponse({"status": "error", "message": "無効なJSONデータです。"}, status=400)
    except Exception as e:  # 予期せぬその他のエラーもキャッチできるように
        print(f"予期せぬエラーが発生しました：{e}")
        # import traceback # 詳細なトレースバックを見たい場合
        # traceback.print_exc()
        return JsonResponse({"status": "error", "message": "サーバー内部エラーが発生しました。"}, status=500)
    # else:
    #     # require_POST デコレータがあるので、通常ここには来ないはず
    #     return JsonResponse({"status": "error", "message": "POSTリクエストのみ許可されています。"}, status=405)

# ▼▼▼ ここ！save_chart_log_view の下に追加するのがキレイ！ ▼▼▼
@method_decorator(login_required, name="dispatch")
class LogListView(ListView):
    model = TroubleshootingSession
    template_name = 'albatross_app/log_list.html'
    context_object_name = 'sessions'
    paginate_by = 10

    def get_queryset(self):
        print("--- get_queryset が呼ばれました！ ---") # ★デバッグログ★
        # まずは、ログインユーザーのログを全部取得
        queryset = TroubleshootingSession.objects.filter(user=self.request.user)

        # --- ▼▼▼ フィルター処理を追加！ ▼▼▼ ---
        
        # 1. チャート種別による絞り込み
        chart_type_id = self.request.GET.get('chart_type')
        if chart_type_id:
            queryset = queryset.filter(chart_type__id=chart_type_id)

        # --- ▼▼▼ 2. 日付範囲による絞り込みを追加！ ▼▼▼ ---
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        period = self.request.GET.get('period')

# 詳細な日付指定がされていれば、そっちを優先！
        if start_date_str or end_date_str:
            if start_date_str:
                queryset = queryset.filter(end_time__gte=start_date_str)
            if end_date_str:
                try: # 無効な日付形式が入力された時のために、エラー処理を追加
                    end_date_datetime = datetime.strptime(end_date_str, '%Y-%m-%d')
                    end_date_plus_one = end_date_datetime + timedelta(days=1)
                    queryset = queryset.filter(end_time__lt=end_date_plus_one)
                    # 詳細な日付指定がなければ、期間ボタンの値をチェック
                except ValueError:
                    pass # 日付形式が不正なら、このフィルターは無視する
        elif period:
            today = timezone.localdate()
            if period == 'today':
                # 今日の0時以降のものを絞り込む
                queryset = queryset.filter(end_time__date=today)
            elif period == 'weekly':
                # 7日前の日付を計算
                seven_days_ago = today - timedelta(days=7)
                # 7日前以降のものを絞り込む
                queryset = queryset.filter(end_time__date__gte=seven_days_ago)
            elif period == 'monthly':
                # 今月の1日以降のものを絞り込む
                queryset = queryset.filter(end_time__year=today.year, end_time__month=today.month)
                # period が 'all' または指定なしの場合は、何もしない (全期間)
        # 4. 最後に、並び順を決定する（これが一番最後！）
        sort_order = self.request.GET.get('sort_order', 'newest')
        if sort_order == 'oldest':
            queryset = queryset.order_by('end_time') # 古い順
        else:
            queryset = queryset.order_by('-end_time') # 新しい順 (デフォルト)
            
        return queryset
        # --- ▲▲▲ 期間の絞り込みここまで ▲▲▲ ---

    def get_context_data(self, **kwargs):
        # --- ▼▼▼ テンプレートに渡す追加情報を定義！ ▼▼▼ ---
        context = super().get_context_data(**kwargs)
        # フィルターのプルダウンメニューで使うために、全チャート種別のリストを渡す
        context['chart_types_for_filter'] = ChartType.objects.all()
        return context

def landing_page_view(request):
    return render(request, "lp/lp2.html")