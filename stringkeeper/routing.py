from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from core import routing as core_routing

from django.conf.urls import url


application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            # example_routing.websocket_urlpatterns,
            core_routing.websocket_urlpatterns,
            
        )
    ),
})
