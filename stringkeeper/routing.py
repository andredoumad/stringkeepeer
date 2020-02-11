from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
# from core import routing as core_routing

from django.conf.urls import url
from chat.consumers import ChatConsumer
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from webharvest.consumers import WebharvestConsumer




application = ProtocolTypeRouter({
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                # example_routing.websocket_urlpatterns,
                # core_routing.websocket_urlpatterns,
                [
                    url(r"^messages/(?P<username>[\w.@+-]+)/$", ChatConsumer),
                    url(r"^messages/(?P<username>[\w.@+-]+)$", ChatConsumer),
                    url(r"^webharvest/$", WebharvestConsumer),
                    url(r"^webharvest$", WebharvestConsumer),
                    url(r"^webharvest/(?P<username>[\w.@+-]+)/$", WebharvestConsumer),
                    url(r"^webharvest/(?P<username>[\w.@+-]+)$", WebharvestConsumer)

                ]
            )
        )
    )
})



# application = ProtocolTypeRouter({
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             # example_routing.websocket_urlpatterns,
#             # core_routing.websocket_urlpatterns,
#             [
#                 url(r"^messages/(?P<username>[\w.@+-]+)/$", ChatConsumer),
#                 url(r"^messages/(?P<username>[\w.@+-]+)$", ChatConsumer)
#             ]
#         )
#     ),
# })


