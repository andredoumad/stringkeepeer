import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer, SyncConsumer
from channels.generic.websocket import WebsocketConsumer

from stringkeeper.standalone_tools import * 
from asgiref.sync import async_to_sync

# def ChatConsumer():
#     eventlog('ChatConsumer! ChatConsumer! ')        


class ChatConsumer(AsyncConsumer):
    eventlog('ChatConsumer! ChatConsumer! ')    
    async def websocket_connect(self, event):
        eventlog('ChatConsumer connected, event: ' + str(event))
        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, event):
        eventlog('ChatConsumer receive, event: ' + str(event))

    async def websocket_disconnect(self, event):
        eventlog('ChatConsumer disconnected, event: ' + str(event))
