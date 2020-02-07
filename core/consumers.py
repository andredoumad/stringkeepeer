
# chat/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer, SyncConsumer
from channels.generic.websocket import WebsocketConsumer
import json
from stringkeeper.braintree_tools import * 
from asgiref.sync import async_to_sync

#works then breaks system
def test_consumer(message):
    eventlog('test_consumer: ' + str(message))


# class EchoConsumer(SyncConsumer):

#     def websocket_connect(self, event):
#         self.send({
#             "type": "websocket.accept",
#         })

#     def websocket_receive(self, event):
#         self.send({
#             "type": "websocket.send",
#             "text": event["text"],
#         })


# def send_channel_message(group_name, message):
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         '{}'.format(group_name),
#         {
#             'type': 'channel_message',
#             'message': message
#         }
#     )



# class ExampleConsumer(AsyncWebsocketConsumer):

#     async def connect(self,msg):
#         # Called on connection.
#         # To accept the connection call:
#         await self.accept()
#         eventlog('EXAMPLE CONSUMER receive ' + 'Channel connected')

#     async def receive(self, data):
#         # do something with data
#         eventlog('EXAMPLE CONSUMER receive ' +  data)
#         # send response back to connected client
#         await self.send('EXAMPLE CONSUMER We received your message')






class EventConsumer(WebsocketConsumer):
    def connect(self):
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        # self.room_group_name = 'chat_%s' % self.room_name
        self.room_name = 'event'
        self.room_group_name = self.room_name+"_sharif"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        print(self.room_group_name)
        self.accept()
        print("#######CONNECTED############")

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        print("DISCONNECED CODE: ",code)

    def receive(self, text_data=None, bytes_data=None):
        print(" MESSAGE RECEIVED")
        data = json.loads(text_data)
        message = data['message']
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,{
                "type": 'send_message_to_frontend',
                "message": message
            }
        )
    def send_message_to_frontend(self,event):
        print("EVENT TRIGERED")
        # Receive message from room group
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))







class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        eventlog('CONNECTED CORE CONNECTED !!!!')
        user_id = self.scope["session"]["_auth_user_id"]
        eventlog('user_id: ' + str(user_id))
        # eventlog('self.scope["session"]["_auth_user_id"]')
        # eventlog(str(self.scope["session"]["_auth_user_id"]))
        
        self.group_name = "{}".format(user_id)
        # Join room group
        eventlog('self.group_name: ' + str(self.group_name))

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        eventlog('DISCONNECTED CORE DISCONNECTED !!!!')
        eventlog('async def disconnect: ' + str(close_code))
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None,bytes_data = None):
        eventlog('RECEIVE CORE RECEIVE !!!!')
        eventlog('async def receive: ' + str(text_data))
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        eventlog("message = text_data_json['message']: " + str(message))
        # Send message to room group
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'receive_group_message',
                'message': message
            }
        )

    async def receive_group_message(self, event):
        eventlog('RECEIVE GROUP MESSAGE CORE !!!!')
        eventlog('async def receive_group_message event: ' + str(event))
        message = event['message']
        eventlog('async def receive_group_message message: ' + str(message))
        # Send message to WebSocket
        await self.send(
             text_data=json.dumps({
            'message': message
        }))