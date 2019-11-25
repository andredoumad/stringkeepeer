
#might want to copy this for the regular user profile too! 
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from stringkeeper.standalone_tools import *
# Create your models here.

User = settings.AUTH_USER_MODEL

class BillingProfile(models.Model):
    user    = models.OneToOneField(User, null=True, blank=True, on_delete='SET_NULL')
    email   = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    # customer_id in Stripe or Braintree 

    def __str__(self):
        return self.email

# def billing_profile_created_receiver(sender, instance, created, *args, **kwargs):
#     if created:
#         eventlog('ACTUAL API REQUEST Send to stripe/braintree')
#         instance.customer_id = newID
#         instance.save()

def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)


post_save.connect(user_created_receiver, sender=User)