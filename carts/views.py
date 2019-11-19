from django.shortcuts import render, redirect
from stringkeeper.standalone_logging import *
from subscription.models import Subscription
from .models import Cart

def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    subscriptions = cart_obj.subscriptions.all()
    total = 0
    for x in subscriptions:
        total += x.price
    eventlog('total: ' + str(total))
    cart_obj.total = total
    cart_obj.save()

    return render(request, "carts/home.html", {})


def cart_update(request):
    eventlog('request.POST: ' + str(request.POST))
    subscription_id = 1
    subscription_obj = Subscription.objects.get(id=1)
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    # eventlog(str(subscription_obj))
    # eventlog(str(vars(subscription_obj)))
    # eventlog(str(vars(cart_obj.subscriptions)))
    # for subscription in cart_obj.subscriptions.all():
    #     eventlog(str(subscription))
    #     eventlog(str('MATCH'))
    if subscription_obj in cart_obj.subscriptions.all():
        cart_obj.subscriptions.remove(subscription_obj)
    else:
        cart_obj.subscriptions.add(subscription_obj)
    # return redirect(subscription_obj.get_absolute_url())
    return redirect("cart:home")