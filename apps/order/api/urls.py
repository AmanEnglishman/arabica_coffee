from django.urls import path
from apps.order.api.views.code import (
    CreateOrderView,
    OrderListView,
    OrderDetailView,
)
from apps.order.api.views.reorder import ReorderView

urlpatterns = [
    path("create/", CreateOrderView.as_view()),
    path("", OrderListView.as_view()),
    path("<int:pk>/", OrderDetailView.as_view()),
    path("<int:order_id>/reorder/", ReorderView.as_view(), name="reorder"),
]
