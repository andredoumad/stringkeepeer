from django.urls import reverse
import math
import datetime
from django.conf import settings
from django.db import models
from django.db.models import Count, Sum, Avg
from django.db.models.signals import pre_save, post_save
from django.utils import timezone

from addresses.models import Address
from billing.models import BillingProfile
from carts.models import Cart
from stringkeeper.standalone_tools import *
from stringkeeper.utils import unique_order_id_generator
from subscription.models import Subscription


ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('active', 'Active'),
    ('expired', 'Expired')
)

class OrderManagerQuerySet(models.query.QuerySet):
    def recent(self):
        return self.order_by("-updated", "-timestamp")

    def get_sales_breakdown(self):
        recent = self.recent().not_is_canceled()
        recent_data = recent.totals_data()
        recent_cart_data = recent.cart_data()
        shipped = recent.not_is_canceled().by_status(status='shipped')
        shipped_data = shipped.totals_data()
        paid = recent.by_status(status='paid')
        paid_data = paid.totals_data()
        data = {
            'recent': recent,
            'recent_data':recent_data,
            'recent_cart_data': recent_cart_data,
            'shipped': shipped,
            'shipped_data': shipped_data,
            'paid': paid,
            'paid_data': paid_data
        }
        return data

    def by_weeks_range(self, weeks_ago=7, number_of_weeks=2):
        if number_of_weeks > weeks_ago:
            number_of_weeks = weeks_ago
        days_ago_start = weeks_ago * 7  # days_ago_start = 49
        days_ago_end = days_ago_start - (number_of_weeks * 7) #days_ago_end = 49 - 14 = 35
        start_date = timezone.now() - datetime.timedelta(days=days_ago_start)
        end_date = timezone.now() - datetime.timedelta(days=days_ago_end) 
        return self.by_range(start_date, end_date=end_date)

    def by_range(self, start_date, end_date=None):
        if end_date is None:
            return self.filter(updated__gte=start_date)
        return self.filter(updated__gte=start_date).filter(updated__lte=end_date)

    def by_date(self):
        now = timezone.now() - datetime.timedelta(days=9)
        return self.filter(updated__day__gte=now.day)

    def totals_data(self):
        return self.aggregate(Sum("total"), Avg("total"))

    def cart_data(self):
        return self.aggregate(
                        Sum("cart__subscriptions__price"), 
                        Avg("cart__subscriptions__price"), 
                        Count("cart__subscriptions")
                                    )

    def by_status(self, status="shipped"):
        return self.filter(status=status)

    def not_is_canceled(self):
        return self.exclude(status='is_canceled')

    def by_request(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile=billing_profile)

    def not_created(self):
        return self.exclude(status='created')


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderManagerQuerySet(self.model, using=self._db)

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def new_or_get(self, billing_profile, cart_obj):
        created = False
        qs = self.get_queryset().filter(
                billing_profile=billing_profile, 
                cart=cart_obj, 
                active=True, 
                status='created'
            )
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = self.model.objects.create(
                    billing_profile=billing_profile, 
                    cart=cart_obj)
            created = True
        return obj, created


# Random, Unique
class Order(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, null=True, blank=True, on_delete=models.SET_NULL)
    order_id    = models.CharField(max_length=120, blank=True)
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', null=True, blank=True, on_delete=models.SET_NULL)
    billing_address = models.ForeignKey(Address, related_name='billing_address', null=True, blank=True, on_delete=models.SET_NULL)
    shipping_address_final    = models.TextField(blank=True, null=True)
    billing_address_final     = models.TextField(blank=True, null=True)
    cart = models.ForeignKey(Cart, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(default=5.99, max_digits=100, decimal_places=2)
    total = models.DecimalField(default=0, max_digits=100, decimal_places=2)
    active = models.BooleanField(default=True)
    updated             = models.DateTimeField(auto_now=True)
    timestamp           = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_id

    objects = OrderManager()

    class Meta:
        ordering = ['-timestamp', '-updated']

    def get_absolute_url(self):
        return reverse("orders:detail", kwargs={'order_id': self.order_id})

    def get_status(self):
        if self.status == "expired":
            return "Expired"
        elif self.status == "active":
            return "Active"
        return "Processing"

    def update_total(self):
        cart_total = self.cart.total
        # shipping total
        new_total = cart_total #plus whatever
        #if your going to add try using fsum
        # like so math.fsum([cart_total, shipping_total])
        # then formatted_total = format(new_total, '.2f')
        self.total = new_total
        self.save()
        return new_total
    
    def check_done(self):
        shipping_address_required = not self.cart.is_digital
        shipping_done = False
        if shipping_address_required and self.shipping_address:
            shipping_done = True
        elif shipping_address_required and not self.shipping_address:
            shipping_done = False
        else:
            shipping_done = True
        billing_profile = self.billing_profile
        # billing_address = self.billing_address
        billing_address = True
        total   = self.total
        eventlog('billing_profile: ' + str(billing_profile))
        eventlog('shipping_done: ' + str(shipping_done))
        eventlog('billing_address: ' + str(billing_address))
        eventlog('total: ' + str(total))
        
        if billing_profile and shipping_done and billing_address and total > 0:
            return True
        return False


    def update_purchases(self):
        for p in self.cart.subscriptions.all():
            obj, created = SubscriptionPurchase.objects.get_or_create(
                    order_id=self.order_id,
                    subscription=p,
                    billing_profile=self.billing_profile
                )
        return SubscriptionPurchase.objects.filter(order_id=self.order_id).count()


    def mark_paid(self):
        if self.status != 'paid':
            if self.check_done():
                self.status = "paid"
                self.save()
                self.update_purchases()
        return self.status
        
#generate order id
def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)

    if instance.shipping_address and not instance.shipping_address_final:
        instance.shipping_address_final = instance.shipping_address.get_address()

    if instance.billing_address and not instance.billing_address_final:
        instance.billing_address_final = instance.billing_address.get_address()

pre_save.connect(pre_save_create_order_id, sender=Order)


def post_save_cart_total(sender, instance, created, *args, **kwargs):
    if not created:
        cart_obj = instance
        cart_total = cart_obj.total
        cart_id = cart_obj.id
        # qs __ means in this cart query lookup by ID 
        qs = Order.objects.filter(cart__id=cart_id)
        if qs.count() == 1:
            order_obj = qs.first()
            order_obj.update_total()

post_save.connect(post_save_cart_total, sender=Cart)

def post_save_order(sender, instance, created, *args, **kwargs):
    eventlog('running')
    if created:
        eventlog('Updating.. first')
        instance.update_total()


post_save.connect(post_save_order, sender=Order)


class SubscriptionPurchaseQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(is_canceled=False)

    def digital(self):
        return self.filter(subscription__is_digital=True)

    def by_request(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile=billing_profile)


class SubscriptionPurchaseManager(models.Manager):
    def get_queryset(self):
        return SubscriptionPurchaseQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def digital(self):
        return self.get_queryset().active().digital()

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def subscriptions_by_id(self, request):
        qs = self.by_request(request).digital()
        ids_ = [x.subscription.id for x in qs]
        return ids_

    def subscriptions_by_request(self, request):
        ids_ = self.subscriptions_by_id(request)
        subscriptions_qs = Subscription.objects.filter(id__in=ids_).distinct()
        return subscriptions_qs

    def subscriptions_by_request_and_billing_profile(self, request, billing_profile):
        ids_ = self.subscriptions_by_id(request)
        subscriptions_qs = Subscription.objects.filter(id__in=ids_).distinct()
        eventlog('subscriptionPurchases for: ' + str(billing_profile))
        subscriptionPurchases_qs = SubscriptionPurchase.objects
        eventlog('subscriptionPurchases_qs: ' + str(subscriptionPurchases_qs))

        for subscriptionPurchase in subscriptionPurchases_qs.all():
            eventlog('subscriptionPurchases_qs.all(): ' + str(subscriptionPurchase))        

        for subscriptionPurchase in subscriptionPurchases_qs.by_request(request):
            eventlog('subscriptionPurchases_qs.by_request(): ' + str(billing_profile) + ' owns ' + str(subscriptionPurchase))
            eventlog(str(billing_profile) + ' order_id is: ' + str(subscriptionPurchase.order_id))
        
        subscriptionPurchases_qs = subscriptionPurchases_qs.by_request(request)
        eventlog('subscriptionPurchase active')
        live_subscription_purchases = []
        for subscriptionPurchase in subscriptionPurchases_qs:
            if subscriptionPurchase.is_canceled == True:
                if subscriptionPurchase.is_canceled_final_date > timezone.now():
                    live_subscription_purchases.append(subscriptionPurchase)
            else:
                live_subscription_purchases.append(subscriptionPurchase)

        return subscriptions_qs, subscriptionPurchases_qs, live_subscription_purchases



class SubscriptionPurchase(models.Model):
    order_id            = models.CharField(max_length=120)
    billing_profile     = models.ForeignKey(BillingProfile, null=True, blank=True, on_delete=models.SET_NULL) # billingprofile.subscriptionpurchase_set.all()
    subscription        = models.ForeignKey(Subscription, null=True, blank=True, on_delete=models.SET_NULL) # subscription.subscriptionpurchase_set.count()
    is_canceled         = models.BooleanField(default=False)
    updated             = models.DateTimeField(auto_now=True)
    timestamp           = models.DateTimeField(auto_now_add=True)
    is_canceled_initial_date      = models.DateTimeField(null=True, blank=True) 
    is_canceled_final_date      = models.DateTimeField(null=True, blank=True)
    braintree_subscription_id = models.CharField(max_length=120, null=True, blank=True)


    objects = SubscriptionPurchaseManager()

    def __str__(self):
        try:
            if self.subscription.title != None:
                return self.subscription.title
        except:
            return str('subscription was deleted')



