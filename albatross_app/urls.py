from django.urls import path
from . import views# viewsモジュールをインポート

from django.http import HttpResponse


app_name = "albatross_app"

def some_testview(request):
    return HttpResponse("ここはalbatross_appの仮ページ")

urlpatterns = [
    # path("dummy_page/", views.some_test_view, name="some_previous_page"),
    path("charts/", views.ChartTypeListView.as_view(), name="chart_type_list"),
    path("chart/<int:chart_type_id>/", views.start_chart_view, name="start_chart"),
    path("save_chart_log/", views.save_chart_log_view, name="save_chart_log"),
    path("lp/", views.landing_page_view, name="landing_page"),
    path("logs/", views.LogListView.as_view(), name="log_list"),
]
# 5/26---ダミーページはコメントアウト
# ↑↑↑ URLは '/app/charts/' みたいになる (プロジェクトのurls.pyで 'app/' を付けてる場合)
#      name='chart_type_list' は、このURLパターンを逆引きする時の名前！
# ↑↑↑チャート種別選択画面のURLパターンをここに追加！
# ↑↑↑ URLは '/app/chart/1/' みたいになる (1 の部分はチャート種別のID)
#      <int:chart_type_id> で、URLの一部を整数としてキャプチャして、ビューの引数に渡してる！
#      name='start_chart' は、chart_type_list.html で使った名前と合わせる！
#5/27---パス3行目追加