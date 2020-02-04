
# chat/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from stringkeeper.braintree_tools import * 

#works then breaks system
def test_consumer(message):
    eventlog('test_consumer: ' + str(message))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        eventlog('CONNECTED CORE CONNECTED !!!!')
        eventlog('CONNECTED CORE CONNECTED !!!!')
        eventlog('CONNECTED CORE CONNECTED !!!!')
        eventlog('async def connect')
        user_id = self.scope["session"]["_auth_user_id"]
        self.group_name = "{}".format(user_id)
        # Join room group

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        eventlog('CONNECTED CORE CONNECTED !!!!')
        eventlog('CONNECTED CORE CONNECTED !!!!')
        eventlog('CONNECTED CORE CONNECTED !!!!')
        eventlog('async def disconnect: ' + str(close_code))
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None,bytes_data = None):
        eventlog('CONNECTED CORE CONNECTED !!!!')
        eventlog('CONNECTED CORE CONNECTED !!!!')
        eventlog('CONNECTED CORE CONNECTED !!!!')
        eventlog('async def receive: ' + str(text_data))
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # Send message to room group
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'recieve_group_message',
                'message': message
            }
        )

    async def recieve_group_message(self, event):
        eventlog('CONNECTED CORE CONNECTED !!!!')
        eventlog('CONNECTED CORE CONNECTED !!!!')
        eventlog('CONNECTED CORE CONNECTED !!!!')
        eventlog('async def recieve_group_message event: ' + str(event))
        message = event['message']
        eventlog('async def recieve_group_message message: ' + str(message))
        # Send message to WebSocket
        await self.send(
             text_data=json.dumps({
            'message': message
        }))