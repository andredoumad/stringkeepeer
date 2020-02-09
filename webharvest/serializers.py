from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from webharvest.models import WebharvestMessageModel
from rest_framework.serializers import ModelSerializer, CharField

from django.contrib.auth import get_user_model
from stringkeeper.standalone_tools import *

User = get_user_model()

class MessageModelSerializer(ModelSerializer):
    # eventlog('MessageModelSerializer')
    user = CharField(source='user.email', read_only=True)
    eventlog('MessageModelSerializer: ' + str(user))
    recipient = CharField(source='recipient.email')

    def create(self, validated_data):
        eventlog('MessageModelSerializer')
        user = self.context['request'].user
        eventlog('user: ' + str(user))

        recipient = get_object_or_404(
            User, email=validated_data['recipient']['email'])

        eventlog('user: ' + str(user))
        corrected_user = user
        AnonymousUser = False
        if str(corrected_user) == str("AnonymousUser"):
            AnonymousUser = True
            eventlog('detected anonymous user!: ' + str(user))
            # corrected_user = User.objects.get(email=recipient)
            corrected_user = User.objects.get(email='andre@stringkeeper.com')


        eventlog('user: ' + str(corrected_user))
        eventlog('user_id: ' + str(corrected_user.id))
        # eventlog('Email: ' + str(email))
        eventlog('Recipient: ' + str(recipient))
        eventlog('validated_data[body] ' + validated_data['body'])
        msg = WebharvestMessageModel(recipient=recipient,
                           body=validated_data['body'],
                           user=corrected_user)
        msg.save()
        # if AnonymousUser == True:
        #     eventlog('AnonymousUser == True: ')
        #     note = msg.notify_ws_clients()
        #     eventlog('note: ' + str(note))
        return msg

    class Meta:
        model = WebharvestMessageModel
        fields = ('id', 'user', 'recipient', 'timestamp', 'body')


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('email',)
