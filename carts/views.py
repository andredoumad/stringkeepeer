from django.shortcuts import render, redirect
from stringkeeper.standalone_tools import *
from orders.models import Order
from subscription.models import Subscription
from .models import Cart
from accounts.forms import LoginForm

def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    return render(request, "carts/home.html", {'cart': cart_obj})


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
        request.session['cart_items'] = cart_obj.subscriptions.count()
        # return redirect(subscription_obj.get_absolute_url())
    return redirect("cart:home")

def checkout_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.subscriptions.count() == 0:
        return redirect('cart:home')
    else:
        order_obj, new_order_obj = Order.objects.get_or_create(cart=cart_obj)
    user = request.user
    billing_profile = None
    login_form = LoginForm()

    if user.is_authenticated:
        billing_profile = None

    context = {
        'object': order_obj,
        'billing_profile': billing_profile,
        'login_form': login_form
    }
    
    return render(request, 'carts/checkout.html', context)