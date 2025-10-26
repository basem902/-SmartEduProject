"""
ASGI config for SmartEduProject with WebSocket support.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize Django ASGI application early
django_asgi_app = get_asgi_application()

# Import routing after Django setup
from apps.projects import routing as project_routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        URLRouter(
            project_routing.websocket_urlpatterns
        )
    ),
})
