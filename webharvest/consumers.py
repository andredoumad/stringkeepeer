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

from django.contrib.auth import get_user_model

from background_task import background
from datetime import datetime

User = get_user_model()

@background(schedule=3600)
def deactivate_webharvest_chat_countdown(user_email):
    eventlog('deactivate_webharvest_chat_countdown')
    eventlog('notify_user has been triggered for ' + str(user_email))
    user = User.objects.get(email=user_email)
    eventlog('notify_user grabbed user object ' + str(user))
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    eventlog(str(user) + ' bool_webharvest_chat_active: ' + str(user.bool_webharvest_chat_active))
    eventlog(str(user) + ' notify user triggered ' + str(dt_string))

    user.bool_webharvest_chat_active = False

    user.save(update_fields=["bool_webharvest_chat_active"])
    eventlog(str(user) + ' bool_webharvest_chat_active: ' + str(user.bool_webharvest_chat_active))


class WebharvestConsumer(AsyncConsumer):
    eventlog('WebharvestConsumer ChatConsumer! WebharvestConsumer ChatConsumer! ')    

    async def websocket_connect(self, event):
        eventlog('WebharvestConsumer ChatConsumer connected, event: ' + str(event))

        me = self.scope['user']

        if str(me) == str('AnonymousUser'):
            eventlog('WSHandler connected, event: ' + str(event))
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
            chat_room = str(me.user_id)
            # chat_room = 'chat_room'
            eventlog('chat_room: ' + str(chat_room))
            self.chat_room = chat_room
            # self.channel_name = 'Human_channel_name'
            me.bool_webharvest_chat_active = True
            # eventlog('channel_name: ' + str(self.channel_name))
            me.save(update_fields=["bool_webharvest_chat_active"])

            await self.channel_layer.group_add(self.chat_room, self.channel_name)

            await self.send({
                "type": "websocket.accept",
            })
            deactivate_webharvest_chat_countdown(me.email)
            my_text = {
                    'message': 'connected to webharvest',
                    'human': str(me.email),
                    'robot_command': 'update_user_status'
            }
            await self.channel_layer.group_send(
                'user_status_updates',
                {
                    'type': 'chat_message',
                    'text': json.dumps(my_text)
                }
            )


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


    async def websocket_receive(self, event):
        eventlog('ChatConsumer receive, event: ' + str(event))

        front_text = event.get('text', None)
        eventlog('front_text: ' + str(front_text))
        loaded_dict_data = json.loads(front_text)
        robot_id = loaded_dict_data.get('robot_id', None)
        eventlog('robot_id: ' + str(robot_id))
        From = loaded_dict_data.get('From', 'stringkeeeper')
        
        # is it a robot ?
        if robot_id != None:
            eventlog('MESSAGE FROM ROBOT')
            # is it a webharvest router ?
            if robot_id != 'webharvest_robot_router':
                eventlog('ROBOT IS NOT ROUTER')
                eventlog("Websocket Receive robot_id: " + str(robot_id))
                robot = loaded_dict_data.get('username', None)
                human = loaded_dict_data.get('human', None)
                thread_obj = await self.get_thread(human, robot)

                self.thread_obj = thread_obj
                eventlog('thread_obj: ' + str(thread_obj))

                # for item in User.objects.all():
                #     eventlog('User: ' + str(item))

                User = get_user_model()
                human_user = User.objects.get(email=human)
                eventlog("DEBUG DEBUG DEBUG DEBUG")
                eventlog('human_user: ' + str(human_user))
                eventlog('human_user.user_id: ' + str(human_user.user_id))

                self.chat_room = str(human_user.user_id)

                # self.chat_room = 'chat_room'
                eventlog('chat_room: ' + str(self.chat_room))
                # self.channel_name = str(human_user.channel_name)
                # self.channel_name = str('Robot_channel_name')
                eventlog('channel_name: ' + str(self.channel_name))


                await self.channel_layer.group_add(self.chat_room, self.channel_name)
            
            # It is a known robot
            else:
                eventlog('ROBOT IS ROUTER COMMAND IS ....')
                robot_command = loaded_dict_data.get('robot_command', None)
                if robot_command == 'get_active_and_inactive_users':
                    active_users = {}
                    inactive_users = {}
                    User = get_user_model()
                    for item in User.objects.all():
                        eventlog('User: ' + str(item))
                        if item.bool_webharvest_chat_active == True:
                            active_users[item.email] = item.webharvest_robot_name
                        else:
                            inactive_users[item.email] = item.webharvest_robot_name
                    # return JsonResponse({
                    #     'active_users': json.dumps(active_users),
                    #     'inactive_users': json.dumps(inactive_users)
                    #     })

                    myResponse = {
                        'active_users': json.dumps(active_users),
                        'inactive_users': json.dumps(inactive_users),
                        'robot_command': 'get_active_and_inactive_users',
                        'From': From
                    }
                    await self.send({                    
                        'type': 'websocket.send',
                        'text': json.dumps(myResponse)
                    })
                elif robot_command == 'set_all_users_to_inactive':
                    User = get_user_model()
                    for user in User.objects.all():
                        eventlog('set_all_users_to_inactive: ' + str(user))
                        user.bool_webharvest_chat_active = False
                        user.save(update_fields=["bool_webharvest_chat_active"])
                elif robot_command == 'subscribe_to_user_status_updates':
                    eventlog('robot_command user_status_updates')
                    await self.channel_layer.group_add('user_status_updates', self.channel_name)


        if robot_id != 'webharvest_robot_router':
            eventlog('ROBOT IS ROBOT')
            eventlog('event: ' + str(event))
            front_text = event.get('text', None)
            loaded_dict_data = json.loads(front_text)

            if front_text is not None:
                msg = loaded_dict_data.get('message', None)
            else:
                msg = 'No message found...'

            if msg != '':
                # msg = 'Message is empty!'

                robot_command = loaded_dict_data.get('robot_command', None)
                eventlog('ROBOT_COMMAND: ' + str(robot_command))
                if robot_command != None:
                    eventlog('ROBOT COMMAND FOUND')
                    if robot_command == 'clear':
                        eventlog('CLEARING CHATROOM MESSAGES')
                        human = loaded_dict_data.get('human', None)
                        robot_id = loaded_dict_data.get('robot_id', None)
                        await self.robot_command_clear(human, robot_id)
                    elif robot_command == 'test_command':
                        eventlog('testing test_command')
                        # human = loaded_dict_data.get('human', None)
                        # robot_id = loaded_dict_data.get('robot_id', None)
                        # await self.robot_command_clear(human, robot_id)
                    msg = 'Processed: ' + msg
                else:
                    eventlog('NO ROBOT COMMAND')





                eventlog('websocket_receive: ' + str(msg) )
                #echo message back to browser
                user = self.scope['user']
                eventlog('websocket_receive: user: ' + str(user) )
                if str(user) == str('AnonymousUser'):
                    robot = loaded_dict_data.get('username', None)
                    human = loaded_dict_data.get('human', None)

                    myResponse = {
                        'message': msg,
                        'username': robot,
                        'From': From
                    }
                    # await self.delete_extra_messages(human, robot)
                    await self.create_chat_message(msg, robot)
                    User = get_user_model()
                    human_user = User.objects.get(email=human)
                    eventlog('websocket_receive: human_user.user_id: ' + str(human_user.user_id))

                    await self.channel_layer.group_send(
                        self.chat_room,
                        {
                            'type': 'chat_message',
                            'text': json.dumps(myResponse)
                        }
                    )
                else:
                    eventlog('websocket_receive: user: ' + str(user) )
                    username = 'default'
                    if user.is_authenticated:
                        username = user.email
                        user.bool_webharvest_chat_active = True
                        user.save(update_fields=["bool_webharvest_chat_active"])
                        deactivate_webharvest_chat_countdown(user.email)
                        my_text = {
                                'message': str(msg),
                                'human': str(username),
                                'robot_command': 'update_user_status',
                                'From': From
                        }
                        await self.channel_layer.group_send(
                            'user_status_updates',
                            {
                                'type': 'chat_message',
                                'text': json.dumps(my_text)
                            }
                        )

                    robot_name = loaded_dict_data.get('robot_name', None)
                    if robot_name != None:
                        eventlog("loaded_dict_data.get('username'): " + str(loaded_dict_data.get('username')))
                        username = robot_name

                    eventlog('websocket_receive: username: ' + str(username) )
                    myResponse = {
                        'message': msg,
                        'username': username,
                        'From': From
                    }
                    await self.create_chat_message(msg, username)

                    # broadcasts message
                    await self.channel_layer.group_send(
                        self.chat_room,
                        {
                            'type': 'chat_message',
                            'text': json.dumps(myResponse)
                        }
                    )

    async def chat_message(self, event):
        eventlog('chat_message: ' + str(event))
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    async def websocket_disconnect(self, event):
        eventlog('disconnected, event: ' + str(event))
        me = self.scope['user']

        if str(me) == str('AnonymousUser'):
            eventlog('AnonymousUser disconnected.')
        else:
            eventlog(str(me) + ' disconnected.')
            me.bool_webharvest_chat_active = True
            # eventlog('channel_name: ' + str(self.channel_name))
            me.save(update_fields=["bool_webharvest_chat_active"])


    #critical decorator -- keeps the database stable 
    @database_sync_to_async
    def get_thread(self, user, other_username):
        eventlog('user ' + str(user) + ' other_username: ' + str(other_username))
        return WebharvestThread.objects.get_or_new(user, other_username)[0]

    @database_sync_to_async
    def create_chat_message(self, msg, username):
        eventlog('create_chat_message msg: ' + str(msg) + ' create_chat_message username: ' + str(username))
        thread_obj   = self.thread_obj
        return WebharvestChatMessage.objects.create(thread=thread_obj, user=username, message=msg)





    async def robot_command_clear(self, human, robot):
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


        # for chat_message in chat_message_list:
        #     try:
        #         eventlog('message: ' + str(chat_message.message))
        #     except:
        #         eventlog('message: ' + str(chat_message) + ' does not have message')
        #         pass
        # delete_old_chats = False
        # if len(chat_message_list) > 5:
        #     delete_old_chats = True
        
        # delete_old_chats = True
        # if delete_old_chats == True:
        #     delete_up_to = len(chat_message_list) - 5
        #     # chat_message_objects = WebharvestChatMessage.objects.filter(thread=thread_obj)

        for i in range(0, len(chat_message_list)):
            eventlog('deleting ' + str(i) + ' of ' + str(len(chat_message_list)))
            eventlog('chat_message_id: ' + str(chat_message_list[i].id))
            WebharvestChatMessage.objects.filter(id=chat_message_list[i].id).delete()
