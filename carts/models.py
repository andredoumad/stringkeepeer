from django.conf import settings
from django.db import models
from stringkeeper.standalone_tools import *
from subscription.models import Subscription
from django.db.models.signals import pre_save, post_save, m2m_changed

User = settings.AUTH_USER_MODEL

class CartManager(models.Manager):
    def new_or_get(self, request):
        cart_id = request.session.get('cart_id', None)
        qs = self.get_queryset().filter(id=cart_id)
        if qs.count() == 1:
            new_obj = False
            eventlog('Cart ID exists')
            cart_obj = qs.first()
            if request.user.is_authenticated == True and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        else:
            cart_obj = Cart.objects.new(user=request.user)
            new_obj = True
            request.session['cart_id'] = cart_obj.id
        return cart_obj, new_obj

    def new(self, user=None):
        eventlog('user authenticated: ' + str(user.is_authenticated))
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)

# Create your models here.
class Cart(models.Model):
    user            = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    subscriptions   = models.ManyToManyField(Subscription, blank=True)
    subtotal        = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    total           = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    updated         = models.DateTimeField(auto_now=True)
    timestamp       = models.DateTimeField(auto_now_add=True)

    objects = CartManager()

    def __str__(self):
        return str(self.id)

    @property
    def name(self):
        return self.user

    @property
    def is_digital(self):
        qs = self.subscriptions.all() #every subscription
        new_qs = qs.filter(is_digital=False) # every subscription that is not digial
        if new_qs.exists():
            return False
        return True

    # @property
    # def is_digital(self):
    #     qs = self.subscriptions.all() #every subscription
    #     new_qs = qs.filter(is_digital=False) # every subscription that is not digial
    #     if new_qs.exists():
    #         return False
    #     return True



def m2m_changed_cart_receiver(sender, instance, action, *args, **kwargs):
    # eventlog('actions: ' + str(action))
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        # eventlog('instance.subscription.all(): ' + str(instance.subscription.all()))
        # eventlog('instance.total: ' + str(instance.total))
        subscriptions = instance.subscriptions.all()
        subtotal = 0
        for x in subscriptions:
            subtotal += x.price
        # eventlog('total: ' + str(total))
        if instance.subtotal != subtotal:
            instance.subtotal = subtotal
            instance.save()


m2m_changed.connect(m2m_changed_cart_receiver, sender=Cart.subscriptions.through)


def pre_save_cart_receiver(sender, instance, *args, **kwargs):
    if instance.subtotal > 0:
        instance.total = float(instance.subtotal) * float(1.08)
    else:
        instance.total = 0.00
pre_save.connect(pre_save_cart_receiver, sender=Cart)











