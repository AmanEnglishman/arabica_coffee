from django.urls import path

from apps.order.crm_views import crm_order_action_view, crm_orders_view


app_name = "crm"

urlpatterns = [
    path("orders/", crm_orders_view, name="orders"),
    path("orders/<int:order_id>/<slug:action>/", crm_order_action_view, name="order-action"),
]
