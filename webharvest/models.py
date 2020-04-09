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
            eventlog('Klass: ' + str(Klass) )
            user2 = Klass.objects.get(robot_name=other_username)
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

    
class WebharvestRobot(models.Model):
    robot_name = models.CharField(max_length=255, blank=True, null=True)
    objects = models.Manager()
    def __str__(self):
        return self.robot_name




class WebharvestThread(models.Model):
    # import WebharvestSpreadSheet
    human        = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name='webharvest_chat_thread_human')
    robot       = models.ForeignKey(WebharvestRobot, null=True, on_delete=models.CASCADE, related_name='webharvest_chat_thread_robot')
    spreadsheet = models.ForeignKey('WebharvestSpreadSheet', null=True, on_delete=models.CASCADE, related_name='webharvest_chat_thread_spreadsheet')
    updated      = models.DateTimeField(auto_now=True)
    timestamp    = models.DateTimeField(auto_now_add=True)
    message_count = models.IntegerField(blank=True, null=True)

    objects      = WebharvestThreadManager()

    def __str__(self):
        value = ''
        if self.human != None:
            value = self.human
        else:
            value = self.updated
        return str(value)

    @property
    def room_group_name(self):
        return str(self.human.user_id)
        # return f'chat_{self.id}'

    # def broadcast(self, msg=None):
    #     if msg is not None:
    #         broadcast_msg_to_chat(msg, group_name=self.room_group_name, user='admin')
    #         return True
    #     return False



class WebharvestChatMessage(models.Model):
    thread      = models.ForeignKey(WebharvestThread, null=True, blank=True, on_delete=models.SET_NULL)
    user        = models.CharField(max_length=255, verbose_name='sender', blank=True, null=True)
    message     = models.TextField()
    timestamp   = models.DateTimeField(auto_now_add=True)

class WebharvestSpreadSheet(models.Model):
    thread      = models.ForeignKey(WebharvestThread, null=True, blank=True, on_delete=models.SET_NULL)
    record_count = models.IntegerField(blank=True, null=True)
    first_row     = models.TextField(blank=True, null=True)
    filepath        = models.CharField(max_length=255, blank=True, null=True)
    timestamp   = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        # value = ''
        # if thread != None:
        #     value = self.human
        # else:
        #     value = self.updated
        return self.thread.human.email


class WebharvestSpreadSheetRecord(models.Model):
    spreadsheet = models.ForeignKey(WebharvestSpreadSheet, null=True, blank=True, on_delete=models.SET_NULL)
    index       = models.IntegerField(blank=True, null=True)
    url    = models.TextField(blank=True, null=True)
    sentence    = models.TextField(blank=True, null=True)
    noun_chunk    = models.TextField(blank=True, null=True)
    lemma    = models.TextField(blank=True, null=True)
    pos    = models.CharField(max_length=32, blank=True, null=True)
    text    = models.TextField(blank=True, null=True)
    label    = models.CharField(max_length=64, blank=True, null=True)


class WebharvestJobManager(models.Manager):

    def get_or_new(self, user):
        eventlog('WebharvestJobManager get_or_new')
        jobs = None
        jobs = WebharvestJob.objects.filter(user_email=user.email)
        # eventlog('jobs: ' + str(jobs))
        # eventlog('len(jobs): ' + str(len(jobs)))
        if len(jobs) >= 1:
            eventlog('RETURNING EXISTING JOB')
            return jobs[0], False
        else:
            eventlog('CREATING NEW JOB')
            obj = self.create(user_email = user.email, job_name = user.email)
            return obj, True
            

        # for item in WebharvestJob.objects.filter(user_email=user.email):
        #     eventlog('for item in WebharvestJob.objects.filter(user_email=user.email):' + str(user.email))
        #     eventlog('item: ' + str(item))
        



class WebharvestJob(models.Model):
    job_name = models.CharField(max_length=255, blank=True, null=True)
    user_email = models.CharField(max_length=255, blank=True, null=True)
    robot_name = models.CharField(max_length=255, blank=True, null=True)
    somesetting = models.CharField(max_length=255, blank=True, null=True)
    search_keywords = models.TextField(blank=True, null=True)
    objects = WebharvestJobManager()
    def __str__(self):
        return self.user_email



