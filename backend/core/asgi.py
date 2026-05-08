"""core/asgi.py"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from notifications import routing as notifications_routing
from messaging import routing as messaging_routing
from core.websocket_auth import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                notifications_routing.websocket_urlpatterns +
                messaging_routing.websocket_urlpatterns
            )
        )
    ),
})
