from django.urls import path
from apps.promotions.api.views import PromotionListView, PromotionDetailView

app_name = "promotions"

urlpatterns = [
    path("", PromotionListView.as_view(), name="promotion-list"),
    path("<int:id>/", PromotionDetailView.as_view(), name="promotion-detail"),
]