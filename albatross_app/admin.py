from django.contrib import admin
from .models import ChartStep, ChartType, TroubleshootingSession, SessionLog, Category# さっき作った ChartStep モデルをインポート！



class ChartStepAdmin(admin.ModelAdmin):
    list_display = ("__str__", "chart_type", "risk_level", "display_order", "is_starting_step", "is_final_step")
    list_filter = ("chart_type", "risk_level", "is_final_step")
    search_fields = ("question_text_beginner", "question_text_intermediate", "keyword_advanced", "solution_text")
    fieldsets =(
        ("基本情報", {
            "fields": ("chart_type", "is_starting_step", "is_final_step")
        }),
        ("質問文（レベル別）", {
            "fields": ("question_text_beginner", "question_text_intermediate", "detailed_explanation")
        }),
        ("分岐設定", {
            "fields": ("yes_next_step", "no_next_step")
        }),
        ("上級モード設定",{
            "fields": ("keyword_advanced", "risk_level", "display_order")
        }),
        ("最終ステップ情報", {
            "fields": ("solution_type",)
        }),
    )



# ★★★ 2. 準備ができたので、ChartStepモデルを登録する！ ★★★
admin.site.register(ChartStep, ChartStepAdmin) # 新しい設定で再登録！
# 以前の単純な admin.site.register(ChartStep) はもう不要なので、この1行だけでOK！
# unregister は、コードを整理する過程で何度も実行エラーになることがあるから、消す

# ★★★ 3. 他のモデルも登録する！ ★★★
# ChartType モデルも管理サイトに登録
admin.site.register(ChartType)
admin.site.register(TroubleshootingSession) #5/27---追記
admin.site.register(SessionLog) #5/27---追記
admin.site.register(Category) #9/7追加