#might want to copy this for the regular user profile too! 
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from stringkeeper.standalone_tools import *
from django.urls import reverse # OLD from django.core.urlresolvers import reverse
# Create your models here.

import requests
from accounts.models import GuestEmail
from django.contrib.postgres.fields import ArrayField


import braintree
User = settings.AUTH_USER_MODEL

STRIPE_BILLING_SERVICE = getattr(settings, 'STRIPE_BILLING_SERVICE', False)

# _STRIPE_
import stripe
stripe.api_key = 'sk_test_UQ6hFgP5OZ9KXeSWvO39jgTb0099ffMFNJ'



BRAINTREE_BILLING_SERVICE = getattr(settings, 'BRAINTREE_BILLING_SERVICE', False)


BRAINTREE_PRODUCTION = getattr(settings, 'BRAINTREE_PRODUCTION', False)
BRAINTREE_MERCHANT_ID = getattr(settings, 'BRAINTREE_MERCHANT_ID', 's7s9hk3y2frmyq6n')
BRAINTREE_PUBLIC_KEY = getattr(settings, 'BRAINTREE_PUBLIC_KEY', 'hnzpmswf3hqpzwtj')
BRAINTREE_PRIVATE_KEY = getattr(settings, 'BRAINTREE_PRIVATE_KEY', '888ebe7f91701688efdc1f9c52471b8f')
BRAINTREE_BILLING_SERVICE = getattr(settings, 'BRAINTREE_BILLING_SERVICE', False)


class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None
        if user.is_authenticated:
            eventlog('logged in user checkout remembers payment stuff')
            obj, created = self.model.objects.get_or_create(user=user, email=user.email, first_name=user.first_name, last_name=user.last_name)
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
    braintree_customer_id = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    braintree_payment_method_token = models.CharField(max_length=255, null=True, blank=True)
    braintree_cardholder_name = models.CharField(max_length=255, null=True, blank=True)
    braintree_masked_number = models.CharField(max_length=255, null=True, blank=True)
    braintree_expiration_date = models.CharField(max_length=255, null=True, blank=True)
    braintree_subscriptions = ArrayField(models.CharField(max_length=50, null=True, blank=True), default=list)
    
    # customer_id in Stripe or Braintree 
    objects = BillingProfileManager()

    def __str__(self):
        return self.email

    def charge(self, order_obj, card=None):
        return Charge.objects.do(self, order_obj, card)

    def get_cards(self): 
        return self.card_set.all()

    def get_payment_method_url(self):
        return reverse('billing-payment-method')

    @property
    def has_card(self): # instance.has_card
        card_qs = self.get_cards()
        return card_qs.exists() # True or False

    @property
    def default_card(self):
        default_cards = self.get_cards().filter(active=True, default=True)
        if default_cards.exists():
            return default_cards.first()
        return None

    def set_cards_inactive(self):
        cards_qs = self.get_cards()
        cards_qs.update(active=False)
        return cards_qs.filter(active=True).count()


def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_receiver, sender=User)



if BRAINTREE_BILLING_SERVICE:
    eventlog('BRAINTREE BILLING SERVICE IS ACTIVE')

    def braintree_billing_profile_created_receiver(sender, instance, *args, **kwargs):

        # === we prime our braintree server gateway here
        gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                environment=settings.BRAINTREE_ENVIRONMENT,
                merchant_id=settings.BRAINTREE_MERCHANT_ID,
                public_key=settings.BRAINTREE_PUBLIC_KEY,
                private_key=settings.BRAINTREE_PRIVATE_KEY
            )
        )
        # get customer
        if not instance.braintree_customer_id and instance.email:
            # https://stripe.com/docs/api/customers/create

            eventlog('instance.first_name: ' + str(instance.first_name)) # correct because it's passed by obj, created = self.model.objects.get_or_create(user=user, email=user.email, first_name=user.first_name, last_name=user.last_name)
            eventlog('instance.last_name: ' + str(instance.last_name)) # correct
            # eventlog('sender.first_name: ' + str(sender.first_name)) # <django.db.models.query_utils.DeferredAttribute object at 0x7f46f6959d30>
            # eventlog('sender.last_name: ' + str(sender.last_name)) # <django.db.models.query_utils.DeferredAttribute object at 0x7f46f6959d90>
            # eventlog('request.first_name: ' + str(request.first_name)) # <django.db.models.query_utils.DeferredAttribute object at 0x7f46f6959d30>
            # eventlog('request.last_name: ' + str(request.last_name)) # <django.db.models.query_utils.DeferredAttribute object at 0x7f46f6959d90>
            eventlog('instance.email: ' + str(instance.email))
            # exit()
            result = gateway.customer.create({
                "first_name": instance.first_name,
                "last_name": instance.last_name,
                "email": instance.email
            })
            eventlog(result)
            instance.braintree_customer_id = result.customer.id


    pre_save.connect(braintree_billing_profile_created_receiver, sender=BillingProfile)
    
    class CardManager(models.Manager):
        def all(self, *args, **kwargs):
            return self.get_queryset().filter(active=True)
        def add_new(self, billing_profile, token):
            if token:
                customer = stripe.Customer.retrieve(billing_profile.braintree_customer_id)
                stripe_card_response = customer.sources.create(source=token)
                new_card = self.model(
                    billing_profile=billing_profile,
                    stripe_id = stripe_card_response.id,
                    brand = stripe_card_response.brand,
                    country = stripe_card_response.country,
                    exp_month = stripe_card_response.exp_month,
                    exp_year = stripe_card_response.exp_year,
                    last4 = stripe_card_response.last4
                ) 
                new_card.save()
                return new_card
            return None

    class Card(models.Model):
        billing_profile         = models.ForeignKey(BillingProfile, null=True, on_delete=models.SET_NULL)
        stripe_id               = models.CharField(max_length=120)
        brand                   = models.CharField(max_length=120, null=True, blank=True)
        country                 = models.CharField(max_length=20, null=True, blank=True)
        exp_month               = models.IntegerField(null=True, blank=True)
        exp_year                = models.IntegerField(null=True, blank=True)
        last4                   = models.CharField(max_length=4, null=True, blank=True)
        default                 = models.BooleanField(default=True)
        active                  = models.BooleanField(default=True)
        timestamp               = models.DateTimeField(auto_now_add=True)

        objects = CardManager()

        def __str__(self):
            return "{} {}".format(self.brand, self.last4)


    def new_card_post_save_receiver(sender, instance, created, *args, **kwargs):
        if instance.default:
            billing_profile = instance.billing_profile
            qs = Card.objects.filter(billing_profile=billing_profile).exclude(pk=instance.pk)
            qs.update(default=False)

    post_save.connect(new_card_post_save_receiver, sender=Card)

    class ChargeManager(models.Manager):
        def do(self, billing_profile, order_obj, card=None): # Charge.objects.do()
            card_obj = card
            if card_obj is None:
                cards = billing_profile.card_set.filter(default=True) # card_obj.billing_profile
                if cards.exists():
                    card_obj = cards.first()
            if card_obj is None:
                return False, "No cards available"
            c = stripe.Charge.create(
                amount = int(order_obj.total * 100), # 39.19 --> 3919
                currency = "usd",
                customer =  billing_profile.stripe_customer_id,
                source = card_obj.stripe_id,
                metadata={"order_id":order_obj.order_id},
                )
            new_charge_obj = self.model(
                    billing_profile = billing_profile,
                    stripe_id = c.id,
                    paid = c.paid,
                    is_canceled = c.is_canceled,
                    outcome = c.outcome,
                    outcome_type = c.outcome['type'],
                    seller_message = c.outcome.get('seller_message'),
                    risk_level = c.outcome.get('risk_level'),
            )
            new_charge_obj.save()
            return new_charge_obj.paid, new_charge_obj.seller_message


    class Charge(models.Model):
        billing_profile         = models.ForeignKey(BillingProfile, null=True, on_delete=models.SET_NULL)
        stripe_id               = models.CharField(max_length=120)
        paid                    = models.BooleanField(default=False)
        is_canceled                = models.BooleanField(default=False)
        outcome                 = models.TextField(null=True, blank=True)
        outcome_type            = models.CharField(max_length=120, null=True, blank=True)
        seller_message          = models.CharField(max_length=120, null=True, blank=True)
        risk_level              = models.CharField(max_length=120, null=True, blank=True)

        objects = ChargeManager()