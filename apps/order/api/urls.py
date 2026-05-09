from django.urls import path

from apps.order.api.views.cancel import CancelOrderView
from apps.order.api.views.code import CreateOrderView, OrderDetailView, OrderListView
from apps.order.api.views.cafe import (
    CafeAssignCourierView,
    CafeMarkDeliveredView,
    CafeMarkReadyView,
    CafeOrderListView,
)
from apps.order.api.views.courier import CourierDeliverView, CourierOrderListView
from apps.order.api.views.reorder import ReorderView
from apps.order.api.views.active_orders import ActiveOrderListView
from apps.order.api.views.reports import OrderReportsView

urlpatterns = [
    # Client
    path("create/",                         CreateOrderView.as_view()),
    path("",                                OrderListView.as_view()),
    path("<int:pk>/",                       OrderDetailView.as_view()),
    path("<int:pk>/cancel/",               CancelOrderView.as_view(),   name="order-cancel"),
    path("<int:order_id>/reorder/",        ReorderView.as_view(),       name="reorder"),
    path("active/",                         ActiveOrderListView.as_view(), name="active-orders"),

    # Cafe staff
    path("cafe/orders/",                                    CafeOrderListView.as_view(),    name="cafe-orders"),
    path("cafe/orders/<int:order_id>/mark-ready/",          CafeMarkReadyView.as_view(),    name="cafe-mark-ready"),
    path("cafe/orders/<int:order_id>/assign-courier/",      CafeAssignCourierView.as_view(), name="cafe-assign-courier"),
    path("cafe/orders/<int:order_id>/mark-delivered/",      CafeMarkDeliveredView.as_view(), name="cafe-mark-delivered"),

    # Courier
    path("courier/orders/",                         CourierOrderListView.as_view(), name="courier-orders"),
    path("courier/orders/<int:order_id>/deliver/",  CourierDeliverView.as_view(),   name="courier-deliver"),

    # Admin
    path("reports/",  OrderReportsView.as_view(), name="order-reports"),
]
