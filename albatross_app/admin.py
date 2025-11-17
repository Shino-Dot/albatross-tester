
from django.contrib import admin
from django.utils.html import format_html # ★★★ format_html をインポート！ ★★★
from .models import ChartStep, ChartType, TroubleshootingSession, SessionLog, Category

class ChartStepAdmin(admin.ModelAdmin):
    
    # ▼▼▼ (1) ここから、魔改造スタート！ ▼▼▼
    
    def short_question(self, obj):
        # (要望③, ④) 質問文を短くして、マウスオーバーで全文表示！
        full_text = obj.question_text_beginner or obj.question_text_intermediate or obj.keyword_advanced
        short_text = (full_text[:20] + '...') if len(full_text) > 20 else full_text
        return format_html('<span title="{}">{}</span>', full_text, short_text)
    
    short_question.short_description = 'チャート内容（マウスオーバーで全文）' # 列のタイトル

    # (要望⑤) 開始/最終ステップの表示を、もっとクールに！
    def is_start_or_final(self, obj):
        if obj.is_starting_step:
            return '🏁 START'
        if obj.display_order % 100 == 99: # display_orderの下2桁が99なら
            return '🏆 GOAL (Success)'
        if obj.display_order % 100 == 98: # display_orderの下2桁が98なら
            return '🚪 ESCAPE'
        return '' # それ以外は、何も表示しない

    is_start_or_final.short_description = '役割' # 列のタイトル
    
    # ▲▲▲ (1) 魔改造、ここまで！ ▲▲▲
    list_display = (
        "display_order",
        "chart_type", 
        "short_question", # ★さっき作った、短い質問文を表示！
        "risk_level", 
        "is_start_or_final", # ★さっき作った、クールな役割表示！
    )
    list_filter = ("chart_type", "risk_level")
    search_fields = ("question_text_beginner", "question_text_intermediate", "keyword_advanced", "solution_text")
    ordering = ("display_order",)
    # ▼▼▼ こいつを、魔改造する！ ▼▼▼
    fieldsets =(
        ("① チャートの基本設定", {
            "fields": (
                "chart_type", 
                "is_starting_step",
            )
        }),
        ("② ステップの役割と順番 ★最重要★", {
            "description": "「2桁+2桁」ルールで番号を付けてね！ (例: カテゴリ01の3番目なら 103、最初の桁が0ゼロの場合は3桁でOK)<br><b>特別ルール:</b> 末尾98は「未解決(ESCAPE)」、99は「解決(GOAL)」用の番号です。",
            "fields": (
                "display_order", 
            )
        }),
        ("③ 質問文（レベル別）", {
            "fields": (
                "question_text_beginner", 
                "question_text_intermediate", 
                "detailed_explanation",
                "keyword_advanced",
                "risk_level",
            )
        }),
        ("④ 分岐設定", {
            "fields": (
                "yes_next_step", 
                "no_next_step",
            )
        }),
        ("⑤ 最終ステップ情報", {
            "classes": ("collapse",), # ★普段は、折りたたんで隠しておく魔法！★
            "fields": (
                "is_final_step",
                "solution_type",
            )
        }),
    )
    # ▲▲▲ 魔改造、ここまで！ ▲▲▲



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