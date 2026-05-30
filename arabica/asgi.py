"""
ASGI config for arabica project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arabica.settings")

django_asgi_app = get_asgi_application()

from apps.order.routing import websocket_urlpatterns as order_ws
from apps.printing.routing import websocket_urlpatterns as printer_ws

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter(order_ws + printer_ws)),
    }
)
