from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from stringkeeper.standalone_tools import *
from orders.models import Order
from subscription.models import Subscription
from accounts.models import GuestEmail
from addresses.forms import AddressCheckoutForm
from .models import Cart
from accounts.forms import LoginForm, GuestForm
from billing.models import BillingProfile
from addresses.models import Address
import stripe


STRIPE_SECRET_KEY = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_UQ6hFgP5OZ9KXeSWvO39jgTb0099ffMFNJ')
STRIPE_PUB_KEY =  getattr(settings, 'STRIPE_PUB_KEY',  'pk_test_k8LAxPXmWxonT6ZUDVxjsuzL00LCGJ2rLX')

stripe.api_key = STRIPE_SECRET_KEY

def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    #converting it 
    eventlog('cart_obj.subscriptions.all(): ' + str(cart_obj.subscriptions.all()))

    # subscriptions = [{'name': x.name, 'price': x.price} for x in cart_obj.subscriptions.all()] 

    # for x in subscriptions:
    #     eventlog('subscription: ' + str(x))

    #this line above is same as the loop below    
    
    subscriptions_list = []
    for x in cart_obj.subscriptions.all():
        subscriptions_list.append(
            {
                'id': x.id,
                'url': x.get_absolute_url(),
                'title': x.title, 
                'price': x.price}
        )

    cart_data = {'subscriptions': subscriptions_list, 'subtotal': cart_obj.subtotal, 'total': cart_obj.total}
    return JsonResponse(cart_data)

def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    eventlog(cart_obj.is_digital)
    context = {
        'cart': cart_obj, 
        'ascii_art': get_ascii_art()
    }
    return render(request, "carts/home.html", context)


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
            added = False
        else:
            eventlog('Adding ' + str(subscription_obj))
            cart_obj.subscriptions.add(subscription_obj)
            added = True

        request.session['cart_items'] = cart_obj.subscriptions.count()
        # return redirect(subscription_obj.get_absolute_url())
        if request.is_ajax(): # Asynchronous javascript and XML / JSON JAVASCRIPT OBJECT NOTATION
            eventlog('ajax request')
            json_data = {
                'added': added,
                'removed': not added,
                'cartItemCount': cart_obj.subscriptions.count()
            }
            return JsonResponse(json_data, status=200) # default status code is 200 -- error is 400 or 500
            #return JsonResponse({'message': 'error'}, status=400) # << emulating an error with message  #Django REST framework is better for doing this kind of thing
            # try using https://craftpip.github.io/jquery-confirm/ for these kind of error messages
            # creates popup menus
    return redirect("cart:home")

def checkout_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.subscriptions.count() == 0:
        return redirect("cart:home")  
    
    login_form = LoginForm(request)
    guest_form = GuestForm(request=request)
    address_form = AddressCheckoutForm()
    billing_address_id = request.session.get("billing_address_id", None)

    shipping_address_required = not cart_obj.is_digital

    shipping_address_id = request.session.get("shipping_address_id", None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None
    has_card = False
    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id) 
            del request.session["billing_address_id"]
        if billing_address_id or shipping_address_id:
            order_obj.save()
        has_card = billing_profile.has_card



    if request.method == "POST":
        "check that order is done"
        is_prepared = order_obj.check_done()
        if is_prepared:
            did_charge, crg_msg = billing_profile.charge(order_obj)
            if did_charge:
                order_obj.mark_paid() # sort a signal for us
                request.session['cart_items'] = 0
                del request.session['cart_id']
                if not billing_profile.user:
                    '''
                    if guest...
                    is this the best spot?
                    '''
                    billing_profile.set_cards_inactive()
                return redirect("cart:success")
            else:
                eventlog(crg_msg)
                return redirect("cart:checkout")
    context = {
        'object': order_obj,
        'billing_profile': billing_profile,
        'login_form': login_form,
        'guest_form': guest_form,
        'address_form': address_form,
        'address_qs': address_qs,
        "has_card": has_card,
        'publish_key': STRIPE_PUB_KEY,
        'ascii_art': get_ascii_art(),
        'shipping_address_required': shipping_address_required
    }
    
    return render(request, 'carts/checkout.html', context)



def checkout_done_view(request):
    context = {
        'ascii_art': get_ascii_art()
    }
    return render(request, 'carts/checkout-done.html', context)