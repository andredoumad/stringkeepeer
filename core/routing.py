from core import consumers

from django.conf.urls import url
# from django.urls import re_path
websocket_urlpatterns = [
    url(r'^ws$', consumers.ChatConsumer),
]



# websocket_urlpatterns = [
#     re_path(r'ws/webharvest/(?P<room_name>\w+)/$', consumers.ChatConsumer),
# ]