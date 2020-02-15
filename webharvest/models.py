from django.db import models

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models import (Model, TextField, DateTimeField, ForeignKey, CASCADE)
from stringkeeper.standalone_tools import *
# from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer

from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model
User = get_user_model()

# FOR A USER AND A BOT
# class WebharvestMessageModel(Model):
#     """
#     This class represents a chat message. It has a owner (user), timestamp and
#     the message body.

#     """
#     user = ForeignKey(User, on_delete=CASCADE, verbose_name='user',
#                       related_name='from_user', db_index=True)
#     recipient = ForeignKey(User, on_delete=CASCADE, verbose_name='recipient',
#                            related_name='to_user', db_index=True)
#     timestamp = DateTimeField('timestamp', auto_now_add=True, editable=False,
#                               db_index=True)
#     body = TextField('body')

#     def __str__(self):
#         return str(self.id)

#     def characters(self):
#         """
#         Toy function to count body characters.
#         :return: body's char number
#         """
#         return len(self.body)

#     def notify_ws_clients(self):
#         """
#         Inform client there is a new message.
#         """
#         notification = {
#             'type': 'receive_group_message',
#             'message': '{}'.format(self.id)
#         }

#         channel_layer = get_channel_layer()
#         eventlog("notify_ws_clients user.id {}".format(self.user.id))
#         eventlog("notify_ws_clients recipient.id {}".format(self.recipient.id))

#         async_to_sync(channel_layer.group_send)("{}".format(self.user.id), notification)
#         async_to_sync(channel_layer.group_send)("{}".format(self.recipient.id), notification)
#         return 'notify_ws_clients ran notify_ws_clients'

#     def save(self, *args, **kwargs):
#         """
#         Trims white spaces, saves the message and notifies the recipient via WS
#         if the message is new.
#         """
#         new = self.id
#         self.body = self.body.strip()  # Trimming whitespaces from the body
#         super(WebharvestMessageModel, self).save(*args, **kwargs)
#         if new is None:
#             self.notify_ws_clients()

#     # Meta
#     class Meta:
#         app_label = 'webharvest'
#         verbose_name = 'message'
#         verbose_name_plural = 'messages'
#         ordering = ('-timestamp',)


class WebharvestThreadManager(models.Manager):
    def by_user(self, user):
        qlookup = Q(human=user) | Q(robot=user)
        qlookup2 = Q(human=user) & Q(robot=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    def get_or_new(self, user, other_username): # get_or_create
        username = user
        if username == other_username:
            eventlog('username == other_username! RETURNING NONE')            
            return None
        eventlog('get_or_new user: ' + str(user))
        eventlog('get_or_new other_username: ' + str(other_username))
        qlookup1 = Q(human__email=username) & Q(robot__robot_name=other_username)
        qlookup2 = Q(human__email=other_username) & Q(robot__robot_name=username)
        eventlog('qlookup1: ' + str(qlookup1))
        eventlog('qlookup2: ' + str(qlookup2))
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        eventlog('qs: ' + str(qlookup2))
        if qs.count() == 1:
            eventlog('qs.count() == 1')
            i = 0
            for item in qs:
                eventlog('qs_item_' + str(i) +' == 1: ' + str(item))
            eventlog('qs.first(): ' + str(qs.first()))
            return qs.first(), False
        elif qs.count() > 1:
            eventlog('qs.count() > 1:')            
            return qs.order_by('timestamp').first(), False
        else:
            eventlog('Creating a new WebharvestThread')
            # Klass = user.__class__
            Klass = WebharvestRobot
            eventlog('Klass is: ' + str(Klass) )
            user2 = Klass.objects.get(robot_name='Alice')
            eventlog("Klass.objects.get(robot_name='Alice'): " + str(user2) )
            if user != user2:
                eventlog('user != user2')
                obj = self.model(
                        human=user, 
                        robot=user2
                    )
                obj.save()
                return obj, True
            return None, False




# class WebharvestThreadManager(models.Manager):

    
class WebharvestRobot(models.Model):
    robot_name = models.CharField(max_length=255, blank=True, null=True)
    objects = models.Manager()
    def __str__(self):
        return self.robot_name


class WebharvestThread(models.Model):
    human        = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name='webharvest_chat_thread_human')
    robot       = models.ForeignKey(WebharvestRobot, null=True, on_delete=models.CASCADE, related_name='webharvest_chat_thread_robot')
    updated      = models.DateTimeField(auto_now=True)
    timestamp    = models.DateTimeField(auto_now_add=True)
    
    objects      = WebharvestThreadManager()

    def __str__(self):
        value = ''
        if self.human != None:
            value = self.human
        else:
            value = updated
        return str(value)

    @property
    def room_group_name(self):
        return str(human.user_id)
        # return f'chat_{self.id}'

    # def broadcast(self, msg=None):
    #     if msg is not None:
    #         broadcast_msg_to_chat(msg, group_name=self.room_group_name, user='admin')
    #         return True
    #     return False



class WebharvestChatMessage(models.Model):
    thread      = models.ForeignKey(WebharvestThread, null=True, blank=True, on_delete=models.SET_NULL)
    # user        = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='sender', on_delete=models.CASCADE)
    user        = models.CharField(max_length=255, verbose_name='sender', blank=True, null=True)
    message     = models.TextField()
    timestamp   = models.DateTimeField(auto_now_add=True)




# def WebharvestChatMessageReceiver(sender, instance, created, *args, **kwargs):
#     eventlog(' TRIGGERED WebharvestChatMessageReceiver TRIGGERED ')

#     channel_layer = get_channel_layer()
#     # async_to_sync(channel_layer.group_send)(
#     #     'thread_1',
#     #     {
#     #         'type': 'send_message_to_frontend',
#     #         'text': str(data['chat_message'])
#     #     }
#     # )
#     my_text = {
#             'message': 'WebharvestChatMessageReceiver testing message',
#             'username': 'Alice'
#     }

#     eventlog(' async_to_sync TRIGGERED WebharvestChatMessageReceiver TRIGGERED async_to_sync ')
#     # async_to_sync(channel_layer.group_send, force_new_loop=False)(
#     #     "testing_channel_name",
#     #     {
#     #         'type': 'chat_message',
#     #         'text': json.dumps(my_text)
#     #     }
#     # )


#     channel_layer.send({
#         'type': 'websocket.send',
#         'text': json.dumps(my_text)
#     })

# post_save.connect(WebharvestChatMessageReceiver, sender=User)





# FOR TWO USERS USING EMAILS



# class WebharvestMessageModel(Model):
#     """
#     This class represents a chat message. It has a owner (user), timestamp and
#     the message body.

#     """
#     user = ForeignKey(User, on_delete=CASCADE, verbose_name='user',
#                       related_name='from_user', db_index=True)
#     recipient = ForeignKey(User, on_delete=CASCADE, verbose_name='recipient',
#                            related_name='to_user', db_index=True)
#     timestamp = DateTimeField('timestamp', auto_now_add=True, editable=False,
#                               db_index=True)
#     body = TextField('body')

#     def __str__(self):
#         return str(self.id)

#     def characters(self):
#         """
#         Toy function to count body characters.
#         :return: body's char number
#         """
#         return len(self.body)

#     def notify_ws_clients(self):
#         """
#         Inform client there is a new message.
#         """
#         notification = {
#             'type': 'receive_group_message',
#             'message': '{}'.format(self.id)
#         }

#         channel_layer = get_channel_layer()
#         eventlog("notify_ws_clients user.id {}".format(self.user.id))
#         eventlog("notify_ws_clients recipient.id {}".format(self.recipient.id))

#         async_to_sync(channel_layer.group_send)("{}".format(self.user.id), notification)
#         async_to_sync(channel_layer.group_send)("{}".format(self.recipient.id), notification)
#         return 'notify_ws_clients ran notify_ws_clients'

#     def save(self, *args, **kwargs):
#         """
#         Trims white spaces, saves the message and notifies the recipient via WS
#         if the message is new.
#         """
#         new = self.id
#         self.body = self.body.strip()  # Trimming whitespaces from the body
#         super(WebharvestMessageModel, self).save(*args, **kwargs)
#         if new is None:
#             self.notify_ws_clients()

#     # Meta
#     class Meta:
#         app_label = 'webharvest'
#         verbose_name = 'message'
#         verbose_name_plural = 'messages'
#         ordering = ('-timestamp',)


# class WebharvestThreadManager(models.Manager):
#     def by_user(self, user):
#         qlookup = Q(first=user) | Q(second=user)
#         qlookup2 = Q(first=user) & Q(second=user)
#         qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
#         return qs

#     def get_or_new(self, user, other_username): # get_or_create
#         username = user
#         if username == other_username:
#             eventlog('username == other_username! RETURNING NONE')            
#             return None
#         eventlog('get_or_new user: ' + str(user))
#         eventlog('get_or_new other_username: ' + str(other_username))
#         qlookup1 = Q(first__email=username) & Q(second__email=other_username)
#         qlookup2 = Q(first__email=other_username) & Q(second__email=username)
#         eventlog('qlookup1: ' + str(qlookup1))
#         eventlog('qlookup2: ' + str(qlookup2))
#         qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
#         eventlog('qs: ' + str(qlookup2))
#         if qs.count() == 1:
#             eventlog('qs.count() == 1')            
#             return qs.first(), False
#         elif qs.count() > 1:
#             eventlog('qs.count() > 1:')            
#             return qs.order_by('timestamp').first(), False
#         else:
#             eventlog('Creating a new WebharvestThread')
#             Klass = user.__class__
#             eventlog('Klass is: ' + str(Klass) )
#             user2 = Klass.objects.get(email=other_username)
#             eventlog('Klass.objects.get(email=other_username): ' + str(user2) )
#             if user != user2:
#                 eventlog('user != user2')
#                 obj = self.model(
#                         first=user, 
#                         second=user2
#                     )
#                 obj.save()
#                 return obj, True
#             return None, False


# class WebharvestThread(models.Model):
#     first        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='webharvest_chat_thread_first')
#     second       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='webharvest_chat_thread_second')
#     updated      = models.DateTimeField(auto_now=True)
#     timestamp    = models.DateTimeField(auto_now_add=True)
    
#     objects      = WebharvestThreadManager()

#     @property
#     def room_group_name(self):
#         return f'chat_{self.id}'

#     def broadcast(self, msg=None):
#         if msg is not None:
#             broadcast_msg_to_chat(msg, group_name=self.room_group_name, user='admin')
#             return True
#         return False


# class WebharvestChatMessage(models.Model):
#     thread      = models.ForeignKey(WebharvestThread, null=True, blank=True, on_delete=models.SET_NULL)
#     user        = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='sender', on_delete=models.CASCADE)
#     message     = models.TextField()
#     timestamp   = models.DateTimeField(auto_now_add=True)