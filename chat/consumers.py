import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer, SyncConsumer
from channels.generic.websocket import WebsocketConsumer

from stringkeeper.standalone_tools import * 
from asgiref.sync import async_to_sync
from .models import Thread, ChatMessage

# def ChatConsumer():
#     eventlog('ChatConsumer! ChatConsumer! ')        


class ChatConsumer(AsyncConsumer):
    eventlog('ChatConsumer! ChatConsumer! ')    
    async def websocket_connect(self, event):
        eventlog('ChatConsumer connected, event: ' + str(event))
        await self.send({
            "type": "websocket.accept",
        })

        # wait 10 seocnds, then close connection
        # await asyncio.sleep(10)
        # await self.send({
        #     'type': 'websocket.close',
        # })
        
        # await channels.auth.get_user(scope)


        me = self.scope['user']
        eventlog("me = self.scope['user']: " + str(me))

        # params = urlparse.parse_qs(message.content['query_string'])
        # eventlog('params = urlparse.parse_qs: ' + str(params))

        # does not work
        other_user = self.scope['url_route']['kwargs']['username']
        eventlog('other_user: ' + str(other_user) + ' me: ' + str(me))  
        thread_obj = await self.get_thread(me, other_user)
        eventlog('thread_obj: ' + str(thread_obj))
        # wait one second then send hello world
        await asyncio.sleep(1)
        await self.send({
            'type': 'websocket.send',
            'text': 'Hello world'
        })



    async def websocket_receive(self, event):
        eventlog('ChatConsumer receive, event: ' + str(event))

    async def websocket_disconnect(self, event):
        eventlog('ChatConsumer disconnected, event: ' + str(event))


    #critical decorator -- keeps the database stable 
    @database_sync_to_async
    def get_thread(self, user, other_username):
        return Thread.objects.get_or_new(user, other_username)[0]
