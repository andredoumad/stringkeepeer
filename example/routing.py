from example import consumers

from django.conf.urls import url
from django.urls import path, re_path
from example.consumers import ws_connect, ws_disconnect, ws_message

websocket_urlpatterns = [
    url(r'^ws$', consumers.ws_connect),
    url(r'^wss$', consumers.ws_connect),
    url(r'^$', consumers.ws_connect),
    path('', consumers.ws_connect),
]

#command=/home/ubuntu/stringkeeper/bin/daphne -e ssl:443:privateKey=/etc/letsencrypt/live/stringkeeper.com/privkey.pem:certKey=/etc/letsencrypt/live/stringkeeper.com/fullchain.pem -b 0.0.0.0 -p 8008 --access-log /home/ubuntu/stringkeeper/daphne.log --proxy-headers stringkeeper.asgi:application