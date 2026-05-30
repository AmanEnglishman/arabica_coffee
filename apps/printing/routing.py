from django.urls import path
from apps.printing.consumers import PrinterConsumer

websocket_urlpatterns = [
    path("ws/printer/", PrinterConsumer.as_asgi()),
]
