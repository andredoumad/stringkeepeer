from core import consumers

from django.conf.urls import url
from django.urls import path, re_path

# THIS WORKS.
websocket_urlpatterns = [
    url(r'^ws$', consumers.ChatConsumer),
    url(r'^wss$', consumers.ChatConsumer),
    # url(r'^ws$', consumers.EchoConsumer),
    # url(r'^wss$', consumers.EchoConsumer),
    # url(r'^ws$', consumers.ExampleConsumer),
    # url(r'^wss$', consumers.ExampleConsumer),
]



# websocket_urlpatterns = [
#     re_path(r'ws/webharvest/(?P<room_name>\w+)/$', consumers.ChatConsumer),
# ]