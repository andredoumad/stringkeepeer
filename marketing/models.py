from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from stringkeeper.standalone_tools import *

from .utils import Mailchimp

class MarketingPreference(models.Model):
    user                        = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    subscribed                  = models.BooleanField(default=True)
    mailchimp_subscribed        = models.NullBooleanField(blank=True)
    mailchimp_msg               = models.TextField(null=True, blank=True)
    timestamp                   = models.DateTimeField(auto_now_add=True)
    updated                      = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user == None:
            return 'user is missing'
        else:
            return self.user.email




def marketing_pref_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        status_code, response_data = Mailchimp().subscribe(instance.user.email)
        eventlog('marketing_pref_create_receiver: ' + str(status_code) + ' ' +str(response_data))


post_save.connect(marketing_pref_create_receiver, sender=MarketingPreference)

def marketing_pref_update_receiver(sender, instance, *args, **kwargs):
    eventlog('marketing_pref_update_receiver triggered')
    if instance.subscribed != instance.mailchimp_subscribed:
        if instance.subscribed:
            # subscribing user
            status_code, response_data = Mailchimp().subscribe(instance.user.email)
            eventlog('marketing_pref_update_receiver triggered subscribe status_code: ' + str(status_code))
            eventlog('instance.user.email: ' + str(instance.user.email))
            Mailchimp().add_email(instance.user.email)
            status_code, response_data = Mailchimp().subscribe(instance.user.email)
            eventlog('marketing_pref_update_receiver triggered subscribe status_code: ' + str(status_code))
        else:
            # unsubscribing user
            status_code, response_data = Mailchimp().unsubscribe(instance.user.email)
            eventlog('marketing_pref_update_receiver triggered unsubscribe status_code: ' + str(status_code))
            eventlog('instance.user.email: ' + str(instance.user.email))
            Mailchimp().add_email(instance.user.email)
            status_code, response_data = Mailchimp().unsubscribe(instance.user.email)
            eventlog('marketing_pref_update_receiver triggered unsubscribe status_code: ' + str(status_code))

        if response_data['status'] == 'subscribed':
            instance.subscribed = True
            instance.mailchimp_subscribed = True
            instance.mailchimp_msg = response_data
        else:
            instance.subscribed = False
            instance.mailchimp_subscribed = False
            instance.mailchimp_msg = response_data

pre_save.connect(marketing_pref_update_receiver, sender=MarketingPreference)



def make_marketing_pref_receiver(sender, instance, created, *args, **kwargs):
    '''
    User model
    '''
    if created:
        MarketingPreference.objects.get_or_create(user=instance)

post_save.connect(make_marketing_pref_receiver, sender=settings.AUTH_USER_MODEL)



