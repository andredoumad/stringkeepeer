import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer, SyncConsumer
from channels.generic.websocket import WebsocketConsumer

from stringkeeper.standalone_tools import * 
from asgiref.sync import async_to_sync
from .models import WebharvestThread, WebharvestChatMessage

# def ChatConsumer():
#     eventlog('ChatConsumer! ChatConsumer! ')        


class WebharvestConsumer(AsyncConsumer):
    eventlog('ChatConsumer! ChatConsumer! ')    
    async def websocket_connect(self, event):
        eventlog('ChatConsumer connected, event: ' + str(event))


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


        # other_user = self.scope['url_route']['kwargs']['username']
        # this is where we get or create a robot, for now we just use Alice.
        other_user = "Alice"
        eventlog('other_user: ' + str(other_user) + ' me: ' + str(me)) 
        thread_obj = await self.get_thread(me, other_user)
        eventlog('thread_obj: ' + str(thread_obj))
        eventlog('me: ' + str(me) + ' thread_obj.id: ' + str(thread_obj.id))
        self.thread_obj = thread_obj
        # chat_room = f"thread_{thread_obj.id}"
        chat_room = str(me.user_id)
        eventlog('chat_room: ' + str(chat_room))
        self.chat_room = chat_room
        eventlog('channel_name: ' + str(self.channel_name))
        # async_to_sync(self.channel_layer.group_add)(chat_room, self.channel_name)
        # await self.accept()
        await self.channel_layer.group_add(chat_room, self.channel_name)
        # await self.accept()

        await self.send({
            "type": "websocket.accept",
        })
        # wait one second then send hello world
        # await asyncio.sleep(1)

    async def websocket_receive(self, event):
        #{'type': 'websocket.receive', 'text': '{"message":"json dater!"}'} 
        eventlog('ChatConsumer receive, event: ' + str(event))
        front_text = event.get('text', None)
        if front_text is not None: 
            loaded_dict_data = json.loads(front_text)
            msg = loaded_dict_data.get('message')
        if front_text is not None and msg != '':
            loaded_dict_data = json.loads(front_text)
            msg = loaded_dict_data.get('message')
            eventlog('websocket_receive: ' + str(msg) )
            #echo message back to browser
            user = self.scope['user']
            eventlog('websocket_receive: user: ' + str(user) )
            username = 'default'
            if user.is_authenticated:
                username = user.email
            
            robot_name = loaded_dict_data.get('robot_name', None)
            eventlog('robot_name: ' + str(robot_name))
            if robot_name != None:
                eventlog('robot_name sent the data')
                eventlog('robot_name: ' + str(robot_name))
                username = robot_name

            eventlog('websocket_receive: username: ' + str(username) )
            myResponse = {
                'message': msg,
                'username': username
            }
            await self.create_chat_message(msg, username)

            # broadcasts message
            await self.channel_layer.group_send(
                self.chat_room,
                # new_event
                {
                    'type': 'chat_message',
                    'text': json.dumps(myResponse)
                }
            )
            # await self.send()

    async def chat_message(self, event):
        eventlog('chat_message: ' + str(event))
        #sends the actual message
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })



    async def chat_message_from_robot(self, event):
        front_text = event.get('text', None)
        loaded_dict_data = json.loads(front_text)
        msg = loaded_dict_data.get('message')
        robot_name = loaded_dict_data.get('username', None)
        await self.create_chat_message(msg, robot_name)
        eventlog('chat_message: ' + str(event))
        #sends the actual message
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })



    async def websocket_disconnect(self, event):
        eventlog('disconnected, event: ' + str(event))

    #critical decorator -- keeps the database stable 
    @database_sync_to_async
    def get_thread(self, user, other_username):
        eventlog('user ' + str(user) + ' other_username: ' + str(other_username))
        return WebharvestThread.objects.get_or_new(user, other_username)[0]

    @database_sync_to_async
    def create_chat_message(self, msg, username):
        eventlog('msg: ' + str(msg) + ' username: ' + str(username))
        thread_obj   = self.thread_obj
        # me           = self.scope['user']
        return WebharvestChatMessage.objects.create(thread=thread_obj, user=username, message=msg)


    async def send_message_to_frontend(self, event):
        eventlog("EVENT TRIGGERED")
        eventlog('event: ' + str(event))
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })


from channels.consumer import SyncConsumer

class LongTask(SyncConsumer):

    def long_task(self, message):
        eventlog(message)