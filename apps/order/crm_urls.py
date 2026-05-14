from django.urls import path

from apps.order.crm_views import (
    crm_couriers_api,
    crm_history_api,
    crm_order_action_view,
    crm_orders_view,
    crm_pos_menu_api,
    crm_pos_order_api,
    crm_pos_view,
    crm_reports_api,
)

app_name = "crm"

urlpatterns = [
    path("orders/", crm_orders_view, name="orders"),
    path("orders/<int:order_id>/<slug:action>/", crm_order_action_view, name="order-action"),
    path("api/history/", crm_history_api, name="api-history"),
    path("api/couriers/", crm_couriers_api, name="api-couriers"),
    path("api/reports/", crm_reports_api, name="api-reports"),
    path("pos/", crm_pos_view, name="pos"),
    path("api/pos/menu/", crm_pos_menu_api, name="api-pos-menu"),
    path("api/pos/order/", crm_pos_order_api, name="api-pos-order"),
]
