from django.db import models

from django.conf import settings
from django.db import models
from django.db.models import Q

from stringkeeper.standalone_tools import *
# from django.contrib.auth import get_user_model

# User = get_user_model()

class WebharvestThreadManager(models.Manager):
    def by_user(self, user):
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    def get_or_new(self, user, other_username): # get_or_create
        username = user
        if username == other_username:
            eventlog('username == other_username! RETURNING NONE')            
            return None
        eventlog('get_or_new user: ' + str(user))
        eventlog('get_or_new other_username: ' + str(other_username))
        qlookup1 = Q(first__email=username) & Q(second__email=other_username)
        qlookup2 = Q(first__email=other_username) & Q(second__email=username)
        eventlog('qlookup1: ' + str(qlookup1))
        eventlog('qlookup2: ' + str(qlookup2))
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        eventlog('qs: ' + str(qlookup2))
        if qs.count() == 1:
            eventlog('qs.count() == 1')            
            return qs.first(), False
        elif qs.count() > 1:
            eventlog('qs.count() > 1:')            
            return qs.order_by('timestamp').first(), False
        else:
            eventlog('qs count is not equal to 1 or greater than 1....')
            Klass = user.__class__
            eventlog('Klass is: ' + str(Klass) )
            user2 = Klass.objects.get(email=other_username)
            eventlog('Klass.objects.get(email=other_username): ' + str(user2) )
            if user != user2:
                eventlog('user != user2')
                obj = self.model(
                        first=user, 
                        second=user2
                    )
                obj.save()
                return obj, True
            return None, False


class WebharvestThread(models.Model):
    first        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='webharvest_chat_thread_first')
    second       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='webharvest_chat_thread_second')
    updated      = models.DateTimeField(auto_now=True)
    timestamp    = models.DateTimeField(auto_now_add=True)
    
    objects      = WebharvestThreadManager()

    @property
    def room_group_name(self):
        return f'chat_{self.id}'

    def broadcast(self, msg=None):
        if msg is not None:
            broadcast_msg_to_chat(msg, group_name=self.room_group_name, user='admin')
            return True
        return False


class WebharvestChatMessage(models.Model):
    thread      = models.ForeignKey(WebharvestThread, null=True, blank=True, on_delete=models.SET_NULL)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='sender', on_delete=models.CASCADE)
    message     = models.TextField()
    timestamp   = models.DateTimeField(auto_now_add=True)