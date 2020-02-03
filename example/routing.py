from example import consumers

from django.conf.urls import url
from django.urls import path, re_path
from example.consumers import ws_connect, ws_disconnect, ws_message
# THIS WORKS.
websocket_urlpatterns = [
    url(r'^ws$', consumers.ws_connect),
    url(r'^wss$', consumers.ws_connect),
]

