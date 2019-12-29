#might want to copy this for the regular user profile too! 
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from stringkeeper.standalone_tools import *
# Create your models here.

from accounts.models import GuestEmail
User = settings.AUTH_USER_MODEL


class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None
        if user.is_authenticated:
            eventlog('logged in user checkout remembers payment stuff')
            obj, created = self.model.objects.get_or_create(user=user, email=user.email)
        elif guest_email_id is not None:
            eventlog('guest user checkout auto reloads payment')
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(email=guest_email_obj.email)
        else:
            eventlog('guest_email_id = ' + str(guest_email_id))
            eventlog('something went wrong here... but we shall continue anyway ')
            pass
        return obj, created

class BillingProfile(models.Model):
    user    = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    email   = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    # customer_id in Stripe or Braintree 
    objects = BillingProfileManager()
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