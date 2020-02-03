import json
# from channels import Group
import threading
import random
from stringkeeper.standalone_tools import *
# def sendmsg(num):
    # Group('stocks').send({'text':num})

t = 0

def periodic():
    global t
    n = random.randint(100,200)
    sendmsg(str(n))
    t = threading.Timer(5, periodic)
    t.start()

def ws_message(message):
    global t
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    print(message.content['text'])
    if ( message.content['text'] == 'start'):
        periodic()
    else:
        t.cancel()
   # message.reply_channel.send({'text':'200'})

def ws_connect(message):
    eventlog('CONNECTED CONNECTED CONNECTED !!! ')
    # Group('stocks').add(message.reply_channel)
    # Group('stocks').send({'text':'connected'})



def ws_disconnect(message):
    pass
    # Group('stocks').send({'text':'disconnected'})
    # Group('stocks').discard(message.reply_channel)