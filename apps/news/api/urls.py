from django.urls import path
from apps.news.api.views import NewsListView, NewsDetailView

app_name = "news"

urlpatterns = [
    path("", NewsListView.as_view(), name="news-list"),
    path("<int:id>/", NewsDetailView.as_view(), name="news-detail"),
]