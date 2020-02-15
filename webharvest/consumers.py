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

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template

# def ChatConsumer():
#     eventlog('ChatConsumer! ChatConsumer! ')        


from django.contrib.auth import get_user_model
User = get_user_model()

class WSHandler(AsyncConsumer):
    eventlog('WSHandler ChatConsumer! WSHandler ChatConsumer! ')

    async def websocket_connect(self, event):
        eventlog('WSHandler connected, event: ' + str(event))
        robot = 'Alice'
        human = 'dante@stringkeeper.com'
        thread_obj = await self.get_thread(human, robot)

        self.thread_obj = thread_obj
        eventlog('thread_obj: ' + str(thread_obj))



        for item in User.objects.all():
            eventlog('User: ' + str(item))


        human_user = User.objects.get(email='dante@stringkeeper.com')
        eventlog('human_user: ' + str(human_user))
        eventlog('human_user.user_id: ' + str(human_user.user_id))
        self.chat_room = str(human_user.user_id)
        # self.chat_room = 'testing_channel_name'
        eventlog('chat_room: ' + str(self.chat_room))
        self.channel_name = str(human_user.channel_name)
        eventlog('channel_name: ' + str(self.channel_name))
        await self.channel_layer.group_add(self.chat_room, self.channel_name)

        await self.send({
            "type": "websocket.accept",
        })

        # myResponse = {
        #     'message': "I'm now connected through websockets, AKA Stargates.",
        #     'username': robot
        # }

        # await self.send({
        #     'type': 'websocket.send',
        #     'text': json.dumps(myResponse)
        # })

    async def websocket_receive(self, event):
        #{'type': 'websocket.receive', 'text': '{"message":"json dater!"}'} 
        eventlog('WSHandler ChatConsumer receive, event: ' + str(event))

        # await self.send({
        #     'type': 'websocket.send',
        #     'text': event['text']
        # })

    # async def chat_message(self, event):
    #     eventlog('chat_message: ' + str(event))
    #     await self.send({
    #         'type': 'websocket.send',
    #         'text': event['text']
    #     })
    #     # # sleep(0.1)


    #critical decorator -- keeps the database stable 
    @database_sync_to_async
    def get_thread(self, user, other_username):
        eventlog('user ' + str(user) + ' other_username: ' + str(other_username))
        return WebharvestThread.objects.get_or_new(user, other_username)[0]


class WebharvestConsumer(AsyncConsumer):
    eventlog('WebharvestConsumer ChatConsumer! WebharvestConsumer ChatConsumer! ')    

    async def websocket_connect(self, event):
        eventlog('WebharvestConsumer ChatConsumer connected, event: ' + str(event))

        me = self.scope['user']
        if str(me) == str('AnonymousUser'):
            eventlog('WSHandler connected, event: ' + str(event))
            robot = 'Alice'
            human = 'dante@stringkeeper.com'
            thread_obj = await self.get_thread(human, robot)

            self.thread_obj = thread_obj
            eventlog('thread_obj: ' + str(thread_obj))

            for item in User.objects.all():
                eventlog('User: ' + str(item))

            human_user = User.objects.get(email='dante@stringkeeper.com')
            eventlog('human_user: ' + str(human_user))
            eventlog('human_user.user_id: ' + str(human_user.user_id))
            # self.chat_room = str(human_user.user_id)
            self.chat_room = 'chat_room'
            eventlog('chat_room: ' + str(self.chat_room))
            # self.channel_name = str(human_user.channel_name)
            # self.channel_name = str('Robot_channel_name')
            eventlog('channel_name: ' + str(self.channel_name))
            await self.channel_layer.group_add(self.chat_room, self.channel_name)

            await self.send({
                "type": "websocket.accept",
            })
        else:
            eventlog("me = self.scope['user']: " + str(me))

            other_user = "Alice"
            eventlog('other_user: ' + str(other_user) + ' me: ' + str(me))
            thread_obj = await self.get_thread(me, other_user)
            eventlog('thread_obj: ' + str(thread_obj))
            eventlog('me: ' + str(me) + ' thread_obj.id: ' + str(thread_obj.id))
            self.thread_obj = thread_obj
            # chat_room = f"thread_{thread_obj.id}"
            # chat_room = str(me.user_id)
            chat_room = 'chat_room'
            eventlog('chat_room: ' + str(chat_room))
            self.chat_room = chat_room
            # self.channel_name = 'Human_channel_name'
            me.channel_name = str(self.channel_name)
            eventlog('channel_name: ' + str(self.channel_name))
            me.channel_name = self.channel_name
            me.save(update_fields=["channel_name"])

            # async_to_sync(self.channel_layer.group_add)(chat_room, self.channel_name)
            # await self.accept()
            await self.channel_layer.group_add(self.chat_room, self.channel_name)
            # await self.accept()

            await self.send({
                "type": "websocket.accept",
            })
            # wait one second then send hello world
            # await asyncio.# sleep(1)


    async def delete_extra_messages(self, human, robot):
        eventlog('delete_extra_messages')
        eventlog('human: ' + str(human) + ' robot: ' + str(robot))
        thread_obj = WebharvestThread.objects.get_or_new(human, robot)[0]

        # self.thread_obj = thread_obj
        eventlog('self.thread_obj: ' + str(thread_obj))
        # delete block start
        chat_message_objects = WebharvestChatMessage.objects.filter(thread=thread_obj)
        eventlog('chat_message_objects: ' + str(chat_message_objects))

        chat_message_list = []

        # for chat_message in chat_message_objects:
        for chat_message in reversed(chat_message_objects):
            chat_message_list.append(chat_message)

        eventlog('length of chat_message_list: ' + str(len(chat_message_list)))

        for chat_message in chat_message_list:
            eventlog('message: ' + str(chat_message))


        for chat_message in chat_message_list:
            try:
                eventlog('message: ' + str(chat_message.message))
            except:
                eventlog('message: ' + str(chat_message) + ' does not have message')
                pass
        delete_old_chats = False
        if len(chat_message_list) > 5:
            delete_old_chats = True


        if delete_old_chats == True:
            delete_up_to = len(chat_message_list) - 5
            # chat_message_objects = WebharvestChatMessage.objects.filter(thread=thread_obj)

            for i in range(0, delete_up_to):
                eventlog('deleting ' + str(i) + ' of ' + str(delete_up_to))
                eventlog('chat_message_id: ' + str(chat_message_list[i].id))
                WebharvestChatMessage.objects.filter(id=chat_message_list[i].id).delete()
        # delete block end
        # await self.send({
        #     'type': 'websocket.send',
        #     'text': 'testing ping'
        # })


    async def websocket_receive(self, event):
        #{'type': 'websocket.receive', 'text': '{"message":"json dater!"}'} 
        eventlog('ChatConsumer receive, event: ' + str(event))

        for item in event:
            eventlog('event item: ' + str(item))
        
        
        eventlog('channel_name: ' + str(self.channel_name))
        eventlog('chat_room: ' + str(self.chat_room))
        eventlog('channel_layer: ' + str(self.channel_layer))

        # await self.send({
        #     'type': 'websocket.send',
        #     'text': str('testing ping... channel_name: ' + str(self.channel_name) + ' chat_room: ' + str(self.chat_room) + ' channel_layer: ' + str(self.channel_layer))
        # })

        # async_to_sync(self.channel_layer.group_send)("testing_channel_name", {"type": "alert.receive"})

        # await self.channel_layer.group_send(
        #     self.chat_room,
        #     {
        #     'type': 'websocket.send',
        #     'text': str('testing ping... channel_name: ' + str(self.channel_name) + ' chat_room: ' + str(self.chat_room) + ' channel_layer: ' + str(self.channel_layer))
        #     }
        # )
        # channel_layer = get_channel_layer()


        # await self.channel_layer.group_send(str(self.channel_name), {
        #     "type": "websocket.send",
        #     "text": "Hello there!",
        # })

        front_text = event.get('text', None)
        if front_text is not None: 
            loaded_dict_data = json.loads(front_text)
            msg = loaded_dict_data.get('message')
        if front_text is not None and msg != '':
            loaded_dict_data = json.loads(front_text)
            msg = loaded_dict_data.get('message', None)
            eventlog('websocket_receive: ' + str(msg) )
            #echo message back to browser
            user = self.scope['user']
            eventlog('websocket_receive: user: ' + str(user) )
            if str(user) == str('AnonymousUser'):
                robot = 'Alice'
                human = 'dante@stringkeeper.com'



                myResponse = {
                    'message': msg,
                    'username': 'Alice'
                }
                await self.delete_extra_messages(human, robot)
                await self.create_chat_message(msg, 'Alice')
                human_user = User.objects.get(email='dante@stringkeeper.com')
                eventlog('websocket_receive: human_user.user_id: ' + str(human_user.user_id) )

                # await self.send({
                #     'type': 'websocket.send',
                #     'text': 'testing ping'
                # })

                await self.channel_layer.group_send(
                    # str(human_user.user_id),
                    self.chat_room,
                    # new_event
                    {
                        'type': 'chat_message',
                        'text': json.dumps(myResponse)
                    }
                )

                # await self.send({
                #     'type': 'websocket.send',
                #     'text': json.dumps(myResponse)
                # })
            else:
                eventlog('websocket_receive: user: ' + str(user) )
                username = 'default'
                if user.is_authenticated:
                    username = user.email


                robot_name = loaded_dict_data.get('robot_name', None)
                if robot_name != None:

                    eventlog("loaded_dict_data.get('username'): " + str(loaded_dict_data.get('username')))
                    username = robot_name

                # await self.delete_extra_messages(user.email, robot_name)


                eventlog('websocket_receive: username: ' + str(username) )
                myResponse = {
                    'message': msg,
                    'username': username
                }
                await self.create_chat_message(msg, username)

                # await self.send({
                #     'type': 'websocket.send',
                #     'text': json.dumps(myResponse)
                # })

                # broadcasts message
                await self.channel_layer.group_send(
                    self.chat_room,
                    # new_event
                    {
                        'type': 'chat_message',
                        'text': json.dumps(myResponse)
                    }
                )

    async def chat_message(self, event):
        eventlog('chat_message: ' + str(event))
        # self.channel_name = 'testing_channel_name'
        eventlog(str('chat_message... channel_name: ' + str(self.channel_name) + ' chat_room: ' + str(self.chat_room) + ' channel_layer: ' + str(self.channel_layer)))
        


        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

        # channel_layer = get_channel_layer()
        # await self.channel_layer.group_send(
        #     'test_channel_name',
        #     {"type": "chat.system_message", "text": 'hi ho'},
        # )


        # await self.channel_layer.group_send(
        #     self.chat_room,
        #     {
        #     'type': 'websocket.send',
        #     'text': str('testing ping... channel_name: ' + str(self.channel_name) + ' chat_room: ' + str(self.chat_room) + ' channel_layer: ' + str(self.channel_layer))
        #     }
        # )

        # # sleep(0.1)


    async def websocket_disconnect(self, event):
        eventlog('disconnected, event: ' + str(event))

    #critical decorator -- keeps the database stable 
    @database_sync_to_async
    def get_thread(self, user, other_username):
        eventlog('user ' + str(user) + ' other_username: ' + str(other_username))
        return WebharvestThread.objects.get_or_new(user, other_username)[0]

    @database_sync_to_async
    def create_chat_message(self, msg, username):
        eventlog('create_chat_message msg: ' + str(msg) + ' create_chat_message username: ' + str(username))

        # self.send({
        #     'type': 'websocket.send',
        #     'text': 'testing ping'
        # })
        thread_obj   = self.thread_obj
        return WebharvestChatMessage.objects.create(thread=thread_obj, user=username, message=msg)

