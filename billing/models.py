#might want to copy this for the regular user profile too! 
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from stringkeeper.standalone_tools import *
# Create your models here.

import requests
from accounts.models import GuestEmail
import logging

logging.basicConfig(level=logging.INFO)


User = settings.AUTH_USER_MODEL
STRIPE_BILLING_SERVICE = getattr(settings, 'STRIPE_BILLING_SERVICE', False)
PAYPAL_BILLING_SERVICE= getattr(settings, 'PAYPAL_BILLING_SERVICE', False)

# _STRIPE_
import stripe
stripe.api_key = 'sk_test_UQ6hFgP5OZ9KXeSWvO39jgTb0099ffMFNJ'

# _PAYPAL_
import paypalrestsdk
from paypalrestsdk import BillingPlan, BillingAgreement, Payment, CreditCard, ResourceNotFound

# paypal stringkeeper sandbox
paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AZ8LR5b_9c_lReQvCfVbj79a6OQe3vdPy_5TbB-IBJ59khQl-IW4dWZq7Zwh2xUjv668fU0G9HDHBPDZ",
  "client_secret": "EHCqz8ZcLHkWPGOvxHnbBFe5obvqtk0zP3R794IMB5A9oBn_Ly-84frwiQg4Db2UBPrjM2hGKyBLoV1Z" })


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
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    paypal_CreditCard_id = models.CharField(max_length=255, null=True, blank=True)
    paypal_BillingPlan_id = models.CharField(max_length=255, null=True, blank=True)
    paypal_BillingAgreementToken = models.CharField(max_length=255, null=True, blank=True)

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


if STRIPE_BILLING_SERVICE:
    eventlog('STRIPE BILLING SERVICE IS ACTIVE')


    def stripe_billing_profile_created_receiver(sender, instance, *args, **kwargs):
        if not instance.stripe_customer_id and instance.email:
            # https://stripe.com/docs/api/customers/create
            customer = stripe.Customer.create(
                email = instance.email

            )
            eventlog(customer)
            instance.stripe_customer_id = customer.id


    pre_save.connect(stripe_billing_profile_created_receiver, sender=BillingProfile)


if STRIPE_BILLING_SERVICE:
    class CardManager(models.Manager):
        
        def add_new(self, billing_profile, token):
            # if str(stripe_card_response.object) == "card":
            if token:
                customer = stripe.Customer.retrieve(billing_profile.stripe_customer_id)
                # https://stripe.com/docs/api/customers/object?lang=python
                card_response = customer.sources.create(source=token)
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
                    refunded = c.refunded,
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
        refunded                = models.BooleanField(default=False)
        outcome                 = models.TextField(null=True, blank=True)
        outcome_type            = models.CharField(max_length=120, null=True, blank=True)
        seller_message          = models.CharField(max_length=120, null=True, blank=True)
        risk_level              = models.CharField(max_length=120, null=True, blank=True)

        objects = ChargeManager()

if PAYPAL_BILLING_SERVICE:
    eventlog('PAYPAL BILLING SERVICE IS ACTIVE')



    def paypal_billing_profile_created_receiver(sender, instance, *args, **kwargs):
        billing_plan_id = None
        eventlog('billing_plan_id: ' + str(instance.paypal_BillingPlan_id))
        if not instance.paypal_CreditCard_id and instance.email:
            # https://github.com/paypal/PayPal-Python-SDK
            # https://developer.paypal.com/docs/subscriptions/
            # https://developer.paypal.com/docs/api/subscriptions/v1/#definition-subscriber
            # https://developer.paypal.com/docs/api/quickstart/create-billing-plan/#create-and-activate-billing-plan
            # https://developer.paypal.com/docs/api/quickstart/create-billing-plan/#define-the-billing-plan-object
            # https://developer.paypal.com/docs/checkout/
            # https://developer.paypal.com/docs/classic/lifecycle/sandbox/sb-test-site/
            # https://www.sandbox.paypal.com/myaccount/summary  >>> andre@blackmesanetwork.com  use this as a test user account
            # https://www.paypal.com/billing/subscriptions

            billing_plan = BillingPlan({
                "name": "Testing1-Regular1",
                "description": "Create Plan for Regular",
                "type": "INFINITE",
                "payment_definitions": [{
                    "name": "Standard Plan",
                    "type": "REGULAR",
                    "frequency_interval": "1",
                    "frequency": "MONTH",
                    "cycles": "0",
                    "amount": {
                    "currency": "USD",
                    "value": "20"
                    }
                }],
                "merchant_preferences": {
                    "auto_bill_amount": "yes",
                    "cancel_url": "http://localhost:3000/cancel",
                    "initial_fail_amount_action": "continue",
                    "max_fail_attempts": "1",
                    "return_url": "http://localhost:3000/processagreement",
                    "setup_fee": {
                    "currency": "USD",
                    "value": "25"
                    }
                }
            })

            # Create billing plan
            if billing_plan.create():
                eventlog("Billing Plan [%s] created successfully" % billing_plan.id)

                # Activate billing plan
                if billing_plan.activate():
                    billing_plan = BillingPlan.find(billing_plan.id)
                    eventlog("Billing Plan [%s] state changed to %s" % (billing_plan.id, billing_plan.state))
                    instance.paypal_BillingPlan_id = billing_plan.id
                else:
                    eventlog(billing_plan.error)
            else:
                eventlog(billing_plan.error)


            # INFO:paypalrestsdk.api:Request[POST]: https://api.sandbox.paypal.com/v1/oauth2/token
            # INFO:paypalrestsdk.api:Response[200]: OK, Duration: 0.386403s.
            # INFO:paypalrestsdk.api:PayPal-Request-Id: 1b7a3d30-58af-4453-8378-bc3665bbfec8
            # INFO:paypalrestsdk.api:Request[POST]: https://api.sandbox.paypal.com/v1/payments/billing-plans
            # INFO:paypalrestsdk.api:Response[201]: Created, Duration: 0.509725s.
            # |-| gkeeper/billing/models.py | 00122 | Billing Plan [P-4B6294309Y477323KMSDQT3Y] created successfully
            # INFO:paypalrestsdk.api:PayPal-Request-Id: 1b7a3d30-58af-4453-8378-bc3665bbfec8
            # INFO:paypalrestsdk.api:Request[PATCH]: https://api.sandbox.paypal.com/v1/payments/billing-plans/P-4B6294309Y477323KMSDQT3Y
            # INFO:paypalrestsdk.api:Response[200]: OK, Duration: 0.639711s.
            # INFO:paypalrestsdk.api:Request[GET]: https://api.sandbox.paypal.com/v1/payments/billing-plans/P-4B6294309Y477323KMSDQT3Y
            # INFO:paypalrestsdk.api:Response[200]: OK, Duration: 0.530034s.
            # |-| gkeeper/billing/models.py | 00127 | Billing Plan [P-4B6294309Y477323KMSDQT3Y] state changed to ACTIVE
            # [02/Jan/2020 04:32:50] "POST /admin/billing/billingprofile/1/change/ HTTP/1.1" 302 0
            # [02/Jan/2020 04:32:51] "GET /admin/billing/billingprofile/1/change/ HTTP/1.1" 200 9962
            # [02/Jan/2020 04:32:52] "GET /admin/jsi18n/ HTTP/1.1" 200 3223

            # eventlog(customer)
            # instance.paypal_customer_id = customer.id

            eventlog('billing_plan_id: ' + instance.paypal_BillingPlan_id)
            billing_agreement = BillingAgreement({
                "name": "Testing1-Regular1",
                "description": "Create Plan for Regular",
                "start_date": "2021-12-22T09:13:49Z",
                "plan": {
                    # "id": "P-0PK90852BK763535UTMSTGMQ"
                    "id": instance.paypal_BillingPlan_id
                },
                "payer": {
                    "payment_method": "paypal"
                },
                "shipping_address": {
                    "line1": "StayBr111idge Suites",
                    "line2": "Cro12ok Street",
                    "city": "San Jose",
                    "state": "CA",
                    "postal_code": "95112",
                    "country_code": "US"
                }
            })


            if billing_agreement.create():
                # Extract redirect url
                token = ''
                for link in billing_agreement.links:
                    eventlog('link: ' + str(link))
                    # https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token=EC-6T414148YR234770S
                    r = requests.get('https://github.com/timeline.json')
                    eventlog('r.json: ' + str(r.json()))
                    eventlog('r.text: ' + str(r.text))
                    
                    if str(link).find('/billing-agreements/'):
                        eventlog('FOUND BILLING AGREEMENT TOKEN!!')
                        token = find_between(str(link), '/billing-agreements/', "/")
                        eventlog('token: ' + str(token))
                        eventlog('YOU NEED TO LET THE USER CLICK AGREE AFTER REDIRECT BEFORE EXECUTING THE FOLLOWING')
                        eventlog('https://github.com/paypal/PayPal-Python-SDK/blob/master/samples/subscription/billing_agreements/execute.py')

                        billing_agreement_response = billing_agreement.execute(str(token))
                        eventlog('billing_agreement_response: ' + str(billing_agreement_response))
                        eventlog("BillingAgreement[%s] executed successfully" % (billing_agreement_response.id))
                    if link.method == "REDIRECT":
                        # Capture redirect url
                        redirect_url = str(link.href)


                        # REDIRECT USER TO redirect_url
                eventlog('billing_agreement.token: ' + str(token))
                instance.paypal_BillingAgreementToken = token
            else:
                eventlog(billing_agreement.error)


            # https://github.com/paypal/PayPal-Python-SDK/blob/master/samples/credit_card/create.py
            credit_card = CreditCard({
                # CreditCard
                # A resource representing a credit card that can be
                # used to fund a payment.
                "external_customer_id": instance.email,
                "type": "visa",
                "number": "4417119669820331",
                "expire_month": "11",
                "expire_year": "2021",
                "cvv2": "874",
                "first_name": "Joe",
                "last_name": "Shopper",

                # Address
                # Base Address object used as shipping or billing
                # address in a payment. [Optional]
                "billing_address": {
                    "line1": "52 N Main ST",
                    "city": "Johnstown",
                    "state": "OH",
                    "postal_code": "43210",
                    "country_code": "US"}})

            # Make API call & get response status
            # Save
            # Creates the credit card as a resource
            # in the PayPal vault.
            if credit_card.create():
                eventlog("CreditCard[%s] created successfully" % (credit_card.id))
                instance.paypal_CreditCard_id = credit_card.id
            else:
                eventlog("Error while creating CreditCard:")
                eventlog(credit_card.error)

            # https://developer.paypal.com/docs/api/orders/v1/?mark=credit_card#definition-credit_card
            try:
                # Retrieve the CreditCard  by calling the
                # static `find` method on the CreditCard class,
                # and pass CreditCard ID
                credit_card = CreditCard.find(credit_card.id)
                eventlog("Got CreditCard[%s]" % (credit_card.id))
                eventlog("CreditCard external_customer_id[%s]" % (credit_card.external_customer_id))
                eventlog("CreditCard Number: [%s]" % (credit_card.number))
                eventlog("CreditCard Type: [%s]" % (credit_card.type))
                eventlog("CreditCard expire_month: [%s]" % (credit_card.expire_month))
                eventlog("CreditCard expire_year: [%s]" % (credit_card.expire_year))
                eventlog("CreditCard cvv2: [%s]" % (credit_card.cvv2))
                eventlog("CreditCard first_name: [%s]" % (credit_card.first_name))
                eventlog("CreditCard last_name: [%s]" % (credit_card.last_name))
                eventlog("CreditCard billing_address: [%s]" % (credit_card.billing_address))
                for a in credit_card.links:
                    eventlog("CreditCard links: [%s]" % (a))
            except ResourceNotFound as error:
                eventlog("CreditCard Not Found")


    pre_save.connect(paypal_billing_profile_created_receiver, sender=BillingProfile)


if PAYPAL_BILLING_SERVICE:
    class CardManager(models.Manager):
        def add_new(self, billing_profile, paypal_card_response):
            if str(paypal_card_response.object) == "card":
                new_card = self.model(
                    billing_profile=billing_profile,
                    paypal_id = paypal_card_response.id,
                    brand = paypal_card_response.type,
                    country = paypal_card_response.country_code,
                    exp_month = paypal_card_response.expire_month,
                    exp_year = paypal_card_response.expire_year,
                    number = paypal_card_response.number
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
        number                   = models.CharField(max_length=4, null=True, blank=True)
        default                 = models.BooleanField(default=True)
        active                  = models.BooleanField(default=True)
        timestamp               = models.DateTimeField(auto_now_add=True)

        objects = CardManager()

        def __str__(self):
            return "{} {}".format(self.brand, self.last4)

