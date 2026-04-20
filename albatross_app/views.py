import json
import collections
from datetime import datetime, timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Case, When

from .models import ChartType, ChartStep, TroubleshootingSession, SessionLog, Category
from django.db import transaction

# ==========================================================
# 1. チャート種別一覧ビュー
# ==========================================================
@method_decorator(login_required, name="dispatch")
class ChartTypeListView(ListView):
    """ログイン後に表示される、カテゴリ別の故障項目選択画面"""
    model = ChartType
    template_name = "albatross_app/chart_type_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # カテゴリを表示順で取得し、関連するチャートタイプを先読み(prefetch)して高速化！
        context['categories_with_charts'] = Category.objects.prefetch_related('charttype_set').all()
        return context

# ==========================================================
# 2. チャート実行ビュー
# ==========================================================
@login_required
def start_chart_view(request, chart_type_id):
    """初級・中級・上級の全モードに対応したチャート表示ロジック"""
    chart_type = get_object_or_404(ChartType, pk=chart_type_id)

    # --- A. 初級/中級用のデータ準備 ---
    # 全ステップを表示順(display_order)で取得
    chart_steps = ChartStep.objects.filter(chart_type=chart_type).order_by("display_order")
    starting_step = chart_steps.filter(is_starting_step=True).first()

    # --- B. 上級用のデータ準備 (リスクレベル順の並べ替え) ---
    all_steps = ChartStep.objects.filter(chart_type=chart_type)
    
    # リスクレベルの重み付けを定義（読みやすく変数化！）
    risk_priority = Case(
        When(risk_level="low", then=1),
        When(risk_level="medium", then=2),
        When(risk_level="high", then=3),
        default=4
    )
    
    normal_steps_query = all_steps.filter(is_final_step=False).order_by(risk_priority, "display_order")
    final_steps = all_steps.filter(is_final_step=True).order_by('display_order')

    # リスクレベルごとにグループ化
    grouped_steps = collections.defaultdict(list)
    for step in normal_steps_query:
        grouped_steps[step.get_risk_level_display()].append(step)

    context = {
        "chart_type": chart_type,
        "chart_steps": chart_steps,
        "starting_step_id_for_js": starting_step.id if starting_step else None,
        "grouped_steps_for_advanced": dict(grouped_steps),
        "final_steps_for_advanced": final_steps,
        "improved_final_step": final_steps.filter(solution_type='improved').first(),
        "unresolved_final_step": final_steps.filter(solution_type='unresolved').first(),
    }
    return render(request, "albatross_app/chart_display.html", context)

# ==========================================================
# 3. ログ保存用API（非同期）
# ==========================================================
@login_required
@require_POST
def save_chart_log_view(request):
    """フロントエンド(JS)からの診断結果を受け取ってDBに保存する"""
    try:
        data = json.loads(request.body)
        chart_type_id = data.get("chart_type_id")
        answers = data.get("answers")
        is_resolved = data.get("is_resolved", True)
        resolved_step_id = data.get("resolved_step_id")

        if chart_type_id is None:
            return JsonResponse({"status": "error", "message": "チャート種別が指定されていません。"}, status=400)

        if not isinstance(answers, dict):
            return JsonResponse({"status": "error", "message": "回答データの形式が不正です。"}, status=400)

        chart_type_obj = get_object_or_404(ChartType, id=int(chart_type_id))

        # 解決ステップの取得（存在する場合）
        resolved_step_obj = None
        if resolved_step_id:
            resolved_step_obj = ChartStep.objects.filter(id=int(resolved_step_id)).first()

        # 1. 先にログリストを組み立てる
        logs_to_create = []
        for step_id_str, answer_value in answers.items():
            try:
                chart_step_obj = ChartStep.objects.get(id=int(step_id_str))
                user_answer = answer_value if answer_value is not None else "unknown"
                logs_to_create.append(SessionLog(
                    chart_step=chart_step_obj,
                    answer=user_answer
                ))
            except (ChartStep.DoesNotExist, ValueError):
                continue

        # 【改善内容】SessionとSessionLogの保存をatomic()で一括化
        # 【改善理由】どちらか一方の保存が失敗した場合に
        #             両方まとめてロールバックされるため、
        #             「親だけ存在して子が0件」というデータ不整合を防ぐ。
        with transaction.atomic():
            session = TroubleshootingSession.objects.create(
                user=request.user,
                chart_type=chart_type_obj,
                is_resolved=is_resolved,
                resolved_step=resolved_step_obj
            )
            # sessionが確定してからlogに紐付けて一括保存
            for log in logs_to_create:
                log.session = session
            SessionLog.objects.bulk_create(logs_to_create)

        return JsonResponse({
            "status": "success",
            "message": f"結果を記録しました。（{len(logs_to_create)}件のログ）"
        })

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "無効なJSONデータです。"}, status=400)
    except Exception as e:
        print(f"致命的なエラーが発生しました：{e}")
        return JsonResponse({"status": "error", "message": "サーバーエラーが発生しました。"}, status=500)

# ==========================================================
# 4. ログ一覧ビュー
# ==========================================================
@method_decorator(login_required, name="dispatch")
class LogListView(ListView):
    """過去の診断ログを閲覧・検索する画面"""
    model = TroubleshootingSession
    template_name = 'albatross_app/log_list.html'
    context_object_name = 'sessions'
    paginate_by = 10

    def get_queryset(self):
        queryset = TroubleshootingSession.objects.filter(user=self.request.user)

        # フィルター処理
        chart_type_id = self.request.GET.get('chart_type')
        if chart_type_id:
            queryset = queryset.filter(chart_type__id=chart_type_id)

        # 日付・期間フィルター
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        period = self.request.GET.get('period')

        if start_date or end_date:
            if start_date: queryset = queryset.filter(end_time__gte=start_date)
            if end_date:
                try:
                    # 終了日の23:59:59まで含めるための処理
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                    queryset = queryset.filter(end_time__lt=end_dt)
                except ValueError: pass
        elif period:
            today = timezone.localdate()
            if period == 'today': queryset = queryset.filter(end_time__date=today)
            elif period == 'weekly': queryset = queryset.filter(end_time__date__gte=today - timedelta(days=7))
            elif period == 'monthly': queryset = queryset.filter(end_time__year=today.year, end_time__month=today.month)

        # 並び順
        sort_order = self.request.GET.get('sort_order', 'newest')
        return queryset.order_by('end_time' if sort_order == 'oldest' else '-end_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chart_types_for_filter'] = ChartType.objects.all()
        return context

# ==========================================================
# 5. その他（LPなど）
# ==========================================================
def landing_page_view(request):
    """ランディングページ表示"""
    return render(request, "lp/lp2.html")