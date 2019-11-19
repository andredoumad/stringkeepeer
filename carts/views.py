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
    subscription_id = request.POST.get('subscription_id')
    if subscription_id is not None:
        try:
            subscription_obj = Subscription.objects.get(id=subscription_id)
        except Subscription.DoesNotExist:
            eventlog('Show Message to user, Subscription is not available.')
            return redirect('cart:home')
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        eventlog('Deciding whether to add or remove item from cart...')
        if subscription_obj in cart_obj.subscriptions.all():
            eventlog('Removing ' + str(subscription_obj))
            cart_obj.subscriptions.remove(subscription_obj)
        else:
            eventlog('Adding ' + str(subscription_obj))
            cart_obj.subscriptions.add(subscription_obj)
        # return redirect(subscription_obj.get_absolute_url())
    return redirect("cart:home")