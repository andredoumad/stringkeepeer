from django.http import JsonResponse
from django.shortcuts import render, redirect
from stringkeeper.standalone_tools import *
from orders.models import Order
from subscription.models import Subscription
from accounts.models import GuestEmail
from addresses.forms import AddressForm
from .models import Cart
from accounts.forms import LoginForm, GuestForm
from billing.models import BillingProfile
from addresses.models import Address


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
                'cartItemCount': cart_obj.subscriptions.count(),
            }
            return JsonResponse(json_data)
    return redirect("cart:home")

def checkout_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.subscriptions.count() == 0:
        return redirect('cart:home')

    user = request.user
    login_form = LoginForm()
    # eventlog('LOGIN_FORM: ' + str(login_form))
    guest_form = GuestForm()
    address_form = AddressForm()
    billing_address_id = request.session.get('billing_address_id', None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None
    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session['billing_address_id']
            order_obj.save()


    if request.method == 'POST':
        eventlog('some check that order is done')
        is_done = order_obj.check_done()
        if is_done:
            order_obj.mark_paid()
            request.session['cart_items'] = 0
            del request.session['cart_id']
            return redirect('cart:success')

    context = {
        'object': order_obj,
        'billing_profile': billing_profile,
        'login_form': login_form,
        'guest_form': guest_form,
        'address_form': address_form,
        'address_qs': address_qs
    }
    
    return render(request, 'carts/checkout.html', context)






def checkout_done_view(request):
    return render(request, 'carts/checkout-done.html', {})