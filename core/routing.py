from core import consumers

from django.conf.urls import url
from django.urls import path, re_path

# THIS WORKS.
websocket_urlpatterns = [
    # url(r'^ws$', consumers.ChatConsumer),
    url(r'^ws$', consumers.ChatConsumer),
    url(r'^wss$', consumers.test_consumer('hello from wss')),
    url(r'^securesockets$', consumers.ChatConsumer),
]



# websocket_urlpatterns = [
#     re_path(r'ws/webharvest/(?P<room_name>\w+)/$', consumers.ChatConsumer),
# ]