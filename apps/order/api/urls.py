from django.urls import path
from apps.order.api.views.code import (
    CreateOrderView,
    OrderListView,
    OrderDetailView,
)
from apps.order.api.views.cafe import (
    CafeOrderListView,
    CafeMarkReadyView,
    CafeAssignCourierView,
    CafeMarkDeliveredView,
)
from apps.order.api.views.courier import (
    CourierOrderListView,
    CourierDeliverView,
)
from apps.order.api.views.reorder import ReorderView

urlpatterns = [
    path("create/", CreateOrderView.as_view()),
    path("", OrderListView.as_view()),
    path("<int:pk>/", OrderDetailView.as_view()),
    path("<int:order_id>/reorder/", ReorderView.as_view(), name="reorder"),
    path("cafe/orders/", CafeOrderListView.as_view(), name="cafe-orders"),
    path("cafe/orders/<int:order_id>/mark-ready/", CafeMarkReadyView.as_view(), name="cafe-mark-ready"),
    path("cafe/orders/<int:order_id>/assign-courier/", CafeAssignCourierView.as_view(), name="cafe-assign-courier"),
    path("cafe/orders/<int:order_id>/mark-delivered/", CafeMarkDeliveredView.as_view(), name="cafe-mark-delivered"),
    path("courier/orders/", CourierOrderListView.as_view(), name="courier-orders"),
    path("courier/orders/<int:order_id>/deliver/", CourierDeliverView.as_view(), name="courier-deliver"),
]
