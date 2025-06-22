from django.db import models
from django.contrib.auth.models import User # Userモデルをインポート
from django.utils import timezone # timezoneをインポート

# 5/27---timezoneと Userモデルをインポート


class ChartType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="チャート種別名",
    )
    description = models.TextField(
        blank=True,
        verbose_name="チャート種別の説明",
    )
    # (任意) このチャート種別の開始ステップ (ChartStepモデルへのOneToOneField)
    # これがあると、「この種類のチャートの最初の質問はコレ！」って直接指定できて便利かも
    # starting_chart_step = models.OneToOneField(
    #     'ChartStep',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='starts_chart_type',
    #     verbose_name="このチャートの開始ステップ"
    # )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "チャート種別"
        verbose_name_plural = "チャート種別"

class ChartStep(models.Model):
    chart_type = models.ForeignKey(
        ChartType, # 上で定義した ChartType モデルを参照
        on_delete=models.CASCADE, # もしチャート種別が削除されたら、関連するステップも全部削除する
        verbose_name="チャート種別"
        # null=True, blank=True を付けるかどうかは、既存データとの兼ね合いで考える
        # (まだ ChartStep にデータがなければ、付けなくてもOKなはず)
    )
# 5/26---この chart_type フィールドをここに追加！ 

# 質問文
    question_text_beginner = models.TextField(
        verbose_name="質問文（初級）",
        blank=True
    )
    question_text_intermediate = models.TextField(
        verbose_name="質問文（中級）",
        blank=True
    )

    # 「はい」を選んだ場合の次のステップ (自分自身のChartStepモデルを参照)
    # null=True, blank=True は、これが最後のステップで「はい」の次がない場合を許容するため
    yes_next_step = models.ForeignKey(
        "self", # 自分自身のモデルを参照
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="goes_to_yes",
        verbose_name="「はい」次のステップ",
    )

    # 「いいえ」を選んだ場合の次のステップ (同様に自分自身を参照)
    no_next_step = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="goes_to_no",
        verbose_name="「いいえ」の場合の次のステップ",
    )

    # これがチャートの開始ステップかどうかを示すフラグ
    is_starting_step = models.BooleanField(
        default=False,
        verbose_name="開始ステップか",
    )

    # これが最終ステップ（解決策提示など）かどうかを示すフラグ
    is_final_step = models.BooleanField(
        default=False,
        verbose_name="最終ステップか",
    )

    # (任意) 最終ステップの場合の解決策やメッセージ
    solution_text = models.TextField(
        blank=True,
        null=True,
        verbose_name="解決策/メッセージ",
    )

    # ▼▼▼ このフィールドを追加！ ▼▼▼
    detailed_explanation = models.TextField(
        blank=True,
        verbose_name="詳細解説（アコーディオン用）"
    )
    # ▲▲▲ ここまで追加！ ▲▲▲

    def __str__(self):
        # まずは初級用の質問文を表示しようと試みる
        display_text = self.question_text_beginner

# もし初級用が空っぽなら、中級用を試みる
        if not display_text:
            display_text = self.question_text_intermediate

# それでも空っぽなら、上級用キーワードを試みる
        if not display_text:
            display_text = self.keyword_advanced

# 最終的に表示するテキストを整形する
# (もし全部空なら「(質問文なし)」になる)
        final_display_text = display_text[:50] if display_text else "(内容未設定)"
        
        type_name = self.chart_type.name if self.chart_type else "(種別未設定)"
        return f"ID: {self.id} - {final_display_text}..."

    
    class Meta:
        verbose_name = "チャートステップ"
        verbose_name_plural = "チャートステップ" # 管理画面での複数形表示名

# 以下6/4追加
    SOLUTION_TYPE_CHOICES = [
        ('improved', '解決/改善'),
        ('unresolved', '未解決/改善なし'),
        ('info', '情報/その他'), # 必要なら
    ]
    solution_type = models.CharField(
        max_length=20,
        choices=SOLUTION_TYPE_CHOICES,
        blank=True, # 空でもOKにするか、デフォルト値を設定するか
        null=True,  # DBレベルでNULLを許可するか
        default=None, # または 'info' とか
        verbose_name='解決タイプ'
    )

    # (1) 上級モード用のキーワード
    keyword_advanced = models.CharField(
        max_length=100,
        blank=True, # キーワードなくてもOKにする
        verbose_name="キーワード（上級）"
    )

    # (2) リスクレベル
    RISK_LEVEL_CHOICES = [
        ("low", "低"),
        ("medium", "中"),
        ("high", "高"),
    ]

    # (3) 表示順序
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES,
        default="low",
        verbose_name="リスクレベル（上級）"
    )

    display_order = models.IntegerField(
        default=0,
        verbose_name="表示順序（上級）",
        help_text="数字が小さいものから順に表示されます。"
    )


    @property
    def solution_type_for_js(self):
        return self.solution_type if self.solution_type else 'unknown'

class TroubleshootingSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ユーザー")
    chart_type = models.ForeignKey(ChartType, on_delete=models.CASCADE, verbose_name="チャート種別")
    end_time = models.DateTimeField(default=timezone.now, verbose_name="完了日時")
    # outcome = models.CharField(max_length=50, blank=True, null=True, verbose_name="結果") # とりあえずコメントアウト

    def __str__(self):
        return f"{self.user.username} - {self.chart_type.name} ({self.end_time.strftime("%Y-%m-%d %H:%M")})"
    
    class Meta:
        verbose_name = "トラブルシューティングセッション"
        verbose_name_plural = "トラブルシューティングセッション"
        ordering = ["-end_time"]


class SessionLog(models.Model):
    session = models.ForeignKey(TroubleshootingSession, related_name="logs", on_delete=models.CASCADE, verbose_name="セッション")
    chart_step = models.ForeignKey(ChartStep, on_delete=models.CASCADE, verbose_name="チャートステップ")
    answer = models.CharField(max_length=10, choices=[("yes", "はい"), ("no", "いいえ"), ("unknown", "不明")], verbose_name="回答")
    # answered_at = models.DateTimeField(default=timezone.now, verbose_name="回答日時") # とりあえずコメントアウト

    def __str__(self):
        return f"{self.session} - Q: {self.chart_step.id} - A: {self.get_answer_display()}"
        # get_answer_display() で choices の表示名を取れる

    class Meta:
        verbose_name = "セッションログ"
        verbose_name_plural = "セッションログ"
        unique_together = ("session", "chart_step") # 同じセッションで同じ質問には1つのログだけ
        