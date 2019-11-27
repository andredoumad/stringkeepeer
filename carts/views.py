from django.shortcuts import render, redirect
from stringkeeper.standalone_tools import *
from orders.models import Order
from subscription.models import Subscription
from accounts.models import GuestEmail
from .models import Cart
from accounts.forms import LoginForm, GuestForm
from billing.models import BillingProfile

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

    user = request.user
    billing_profile = None
    login_form = LoginForm()
    # eventlog('LOGIN_FORM: ' + str(login_form))
    guest_form = GuestForm()
    guest_email_id = request.session.get('guest_email_id')

    if user.is_authenticated:
        eventlog('logged in user checkout remembers payment stuff')
        if user.email:
            billing_profile, billing_profile_created = BillingProfile.objects.get_or_create(user=user, email=user.email)
    elif guest_email_id is not None:
        eventlog('guest user checkout auto reloads payment')
        guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
        billing_profile, billing_guest_profile_created = BillingProfile.objects.get_or_create(email=guest_email_obj.email)
    else:
        eventlog('guest_email_id = ' + str(guest_email_id))
        eventlog('something went wrong here... but we shall continue anyway ')
        pass


    if billing_profile is not None:
        order_obj, order_obj_created = Order.objects.new_org_get(billing_profile, cart_obj)
        # order_qs = Order.objects.filter(billing_profile=billing_profile, cart=cart_obj, active=True)
        # if order_qs.count()== 1:
        #     order_obj = order_qs.first()
        # else:
        #     order_obj = Order.objects.create(billing_profile=billing_profile, cart=cart_obj)







    context = {
        'object': order_obj,
        'billing_profile': billing_profile,
        'login_form': login_form,
        'guest_form': guest_form
    }
    
    return render(request, 'carts/checkout.html', context)

