from django.urls import path

from apps.order.consumers import CafeOrdersConsumer


websocket_urlpatterns = [
    path("ws/crm/orders/", CafeOrdersConsumer.as_asgi()),
]
