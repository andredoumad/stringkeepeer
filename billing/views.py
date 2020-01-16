from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
from stringkeeper.standalone_tools import *
from django.utils.http import is_safe_url
from .models import BillingProfile, Card
from orders.models import Order
from carts.models import Cart
from .forms import PaymentMethodForm

import braintree
from .extras import generate_order_id, transact, generate_client_token

# _STRIPE_
import stripe

STRIPE_BILLING_SERVICE = getattr(settings, 'STRIPE_BILLING_SERVICE', False)
STRIPE_SECRET_KEY = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_UQ6hFgP5OZ9KXeSWvO39jgTb0099ffMFNJ')
STRIPE_PUB_KEY =  getattr(settings, 'STRIPE_PUB_KEY',  'pk_test_k8LAxPXmWxonT6ZUDVxjsuzL00LCGJ2rLX')


stripe.api_key = STRIPE_SECRET_KEY


if STRIPE_BILLING_SERVICE:

    def payment_method_view(request):
        eventlog('STRIPE - payment_method_view')
        # if request.user.is_authenticated:
        #     billing_profile = request.user.billingprofile
        #     my_customer_id = billing_profile.customer_id

        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

        if not billing_profile:
            return redirect("/cart")

        next_url = None
        next_ = request.GET.get('next')
        if is_safe_url(next_, request.get_host()):
            next_url = next_


        context = {
            'publish_key': STRIPE_PUB_KEY,
            'next_url': next_url, 
            'payment_company': 'stripe',
            'ascii_art': get_ascii_art()
            }

        return render(request, 'billing/payment-method.html', context)


    #unique to braintree -- referenced in a from import -- so we pass
    def payment():
        pass


    def payment_method_createview(request):
        eventlog('STRIPE - payment_method_createview')
        if request.method == "POST" and request.is_ajax():
            eventlog(request.POST)
            billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
            if not billing_profile:
                return HttpResponse({"message": "Cannot find this user"}, status_code=401)
            token = request.POST.get("token")
            if token is not None:
                new_card_obj = Card.objects.add_new(billing_profile, token)
                eventlog(new_card_obj) # this is where we start saving our cards too!

            return JsonResponse({"message": "Success your card was added !!"})
        return HttpResponse("error", status_code=401)



BRAINTREE_PRODUCTION = getattr(settings, 'BRAINTREE_PRODUCTION', False)
BRAINTREE_MERCHANT_ID = getattr(settings, 'BRAINTREE_MERCHANT_ID', 's7s9hk3y2frmyq6n')
BRAINTREE_PUBLIC_KEY = getattr(settings, 'BRAINTREE_PUBLIC_KEY', 'hnzpmswf3hqpzwtj')
BRAINTREE_PRIVATE_KEY = getattr(settings, 'BRAINTREE_PRIVATE_KEY', '888ebe7f91701688efdc1f9c52471b8f')
BRAINTREE_BILLING_SERVICE = getattr(settings, 'BRAINTREE_BILLING_SERVICE', False)

if BRAINTREE_BILLING_SERVICE:
    eventlog('BRAINTREE BILLING SERVICE IS ACTIVE')
    def payment_method_view(request):
        eventlog('BRAINTREE - payment_method_view')
        # if request.user.is_authenticated:
        #     billing_profile = request.user.billingprofile
        #     my_customer_id = billing_profile.customer_id

        gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                environment=settings.BRAINTREE_ENVIRONMENT,
                merchant_id=settings.BRAINTREE_MERCHANT_ID,
                public_key=settings.BRAINTREE_PUBLIC_KEY,
                private_key=settings.BRAINTREE_PRIVATE_KEY
            )
        )
        user_first_name = str(request.user.first_name)
        user_last_name = str(request.user.last_name)
        user_email = str(request.user.email)

        eventlog('user first name: ' + user_first_name)
        eventlog('user last name: ' + user_last_name)
        eventlog('user email: ' + user_email)

        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        eventlog('billing_profile: ' + str(billing_profile))
        eventlog('billing_profile_created: ' + str(billing_profile_created))

        billing_profile_first_name = str(billing_profile.first_name)
        eventlog('billing_profile_first_name: ' + billing_profile_first_name)
        billing_profile_last_name = str(billing_profile.last_name)
        eventlog('billing_profile_last_name: ' + billing_profile_last_name)
        billing_profile_street = str(billing_profile.street)
        eventlog('billing_profile_street: ' + billing_profile_street)
        billing_profile_postal_code = str(billing_profile.postal_code)
        eventlog('billing_profile_postal_code: ' + billing_profile_postal_code)

        braintree_customer_id = billing_profile.braintree_customer_id
        eventlog('braintree_customer_id: ' + str(braintree_customer_id))


        if braintree_customer_id == None:
            eventlog('braintree_customer_id is None, creating customer')
            result = gateway.customer.create({
                "first_name": user_first_name,
                "last_name": user_last_name,
                "email": user_email
            })

            if result.is_success:
                eventlog('braintree_customer_id created.')
                customer_id = result.customer.id
                eventlog('braintree_customer_id changed from: ' + str(billing_profile.braintree_customer_id))
                billing_profile.braintree_customer_id = customer_id
                eventlog('to: ' + str(billing_profile.braintree_customer_id))
                braintree_customer_id = customer_id
                billing_profile.save(update_fields=["braintree_customer_id"]) 

        collection = gateway.customer.search(
            braintree.CustomerSearch.id == braintree_customer_id
        )
        i = 0
        for customer in collection.items:
            eventlog('customer: ' + str(customer))
            eventlog('braintree_customer ' + str(i) + ' first_name: ' + str(customer.first_name))
            braintree_customer_first_name = str(customer.first_name)
            eventlog('braintree_customer ' + str(i) + ' last_name: ' + str(customer.last_name))
            braintree_customer_last_name = str(customer.last_name)
            eventlog('braintree_customer ' + str(i) + ' email: ' + str(customer.email))
            braintree_customer_email = str(customer.email)
            i += 1

        eventlog('collection: ' + str(collection))

        eventlog('braintree_customer_first_name: ' + braintree_customer_first_name)        
        eventlog('braintree_customer_last_name: ' + braintree_customer_last_name)
        eventlog('braintree_customer_email: ' + braintree_customer_email)

        cart, cart_created = Cart.objects.new_or_get(request)
        eventlog('cart: ' + str(cart))
        eventlog('cart_created: ' + str(cart_created))

        order_profile, order_profile_created = Order.objects.new_or_get(billing_profile, cart)
        eventlog('order_profile: ' + str(order_profile))
        order_billing_address = order_profile.billing_address
        eventlog('order_billing_address: ' + str(order_billing_address))
        eventlog('order_profile_created: ' + str(order_profile_created))

        if not billing_profile:
            return redirect("/cart")

        next_url = None
        next_ = request.GET.get('next')
        if is_safe_url(next_, request.get_host()):
            next_url = next_

        client_token = gateway.client_token.generate({
            "customer_id": braintree_customer_id
        })
        eventlog('client_token: ' + str(client_token))
        
        payment_method_nonce = ''
        # payment_method_nonce = str(request.form['payment_method_nonce'])
        # eventlog('request.form[payment_method_nonce]: ' + payment_method_nonce)

        success_token = ''
        # paymentform = PaymentMethodForm( request.POST or None, initial={
        #         'first_name': billing_profile_first_name,
        #         'last_name': billing_profile_last_name,
        #         'street': billing_profile_street,
                
        #         })

        paymentform = PaymentMethodForm( request.POST or None, initial={
                'first_name': billing_profile_first_name,
                'last_name': billing_profile_last_name,
                'street': billing_profile_street,
                'postal_code': billing_profile_postal_code
                
                })
        # form.fields["first_name"] = user_first_name 

        if request.method == 'POST':
            testvariable = request.POST.get('testvariable')
            eventlog('testvariable: ' + str(testvariable))

            payload = request.POST.get('payload')
            eventlog('payload: ' + str(payload))

            nonce = request.POST.get('nonce')
            eventlog('nonce: ' + str(nonce))

            eventlog('request.method: ' + str(request.method))

            eventlog('paymentform.first_name: ' + str(request.POST.get('first_name', None)))
            billing_profile.first_name = request.POST.get('first_name', None)
            eventlog('paymentform.last_name: ' + str(request.POST.get('last_name', None)))
            billing_profile.last_name = request.POST.get('last_name', None)
            eventlog('paymentform.street: ' + str(request.POST.get('street', None)))
            billing_profile.street = request.POST.get('street', None)
            eventlog('paymentform.postal_code: ' + str(request.POST.get('postal_code', None)))
            billing_profile.postal_code = request.POST.get('postal_code', None)
            billing_profile.save(
                update_fields=[
                    "first_name",
                    "last_name",
                    "street",
                    "postal_code"
                    ])
            
            # result = gateway.payment_method_nonce.create("A_PAYMENT_METHOD_TOKEN")
            # nonce = result.payment_method_nonce.nonce
            
            payment_method_nonce = request.POST.get('payment_method_nonce')
            eventlog('payment_method_nonce: ' + str(payment_method_nonce))
            result = gateway.customer.update(braintree_customer_id, {
                "payment_method_nonce": payment_method_nonce,
                "email": request.user.email,
                # fake credit card 4012000077777777
                # another fake 4111111111111111
                "credit_card": {
                    "options": {
                        "update_existing_token": client_token,
                    },
                    "billing_address": {
                        "street_address": billing_profile.street,
                        "postal_code": billing_profile.postal_code,
                        "options": {
                            "update_existing": True
                        }
                    }
                }
            })

            eventlog('result: ' + str(result))



            # payment_method_token = result.payment_method.token
            # eventlog('result.payment_method.token: ' + str(payment_method_token))

            # payment_method_token = result.customer.payment_methods[0].token
            # eventlog('result.customer.payment_methods[0].token: ' + str(payment_method_token))

            # nonce = result.payment_method_nonce.nonce

            # eventlog('nonce: ' + str(nonce))

            # collection = gateway.customer.search(
            #     braintree.CustomerSearch.id == braintree_customer_id
            # )

            # for customer in collection.items:
            #     payment_method_token = customer.payment_method_token 
            #     eventlog('payment_method_token: ' + str(payment_method_token))




        context = {
            'paymentform': paymentform,
            
            'user_first_name': user_first_name,
            'user_last_name': user_last_name,
            'user_email': user_email,

            'billing_profile': str(billing_profile),
            'billing_profile_created': str(billing_profile_created),
            'billing_profile_first_name': str(billing_profile_first_name),
            'billing_profile_last_name': str(billing_profile_last_name),
            'billing_profile_street': str(billing_profile_street),
            'billing_profile_postal_code': str(billing_profile_postal_code),
            'braintree_customer_id': str(braintree_customer_id),

            'collection': str(collection),
            'braintree_customer_first_name': braintree_customer_first_name,
            'braintree_customer_last_name': braintree_customer_last_name,
            'braintree_customer_email': braintree_customer_email,

            'cart': str(cart),
            'cart_created': str(cart_created),

            'order_profile': str(order_profile),
            'order_profile_created': str(order_profile_created), 
            'order_billing_address': str(order_billing_address),   


            'payment_company': 'braintree',
            'client_token': str(client_token),
            'ascii_art': get_ascii_art()
            }
        eventlog(' ABOUT TO HIT LINE 94 ')
        return render(request, 'billing/payment-method.html', context)


    # def update_transaction_records(request, token):
    #     eventlog('token: ' + str(token))
    #     pass






    def payment(request):
        nonce_from_the_client = request.POST['paymentMethodNonce']
        customer_kwargs = {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        }
        customer_create = braintree.Customer.create(customer_kwargs)
        customer_id = customer_create.customer.id
        result = braintree.Transaction.sale({
            "amount": "10.00",
            "payment_method_nonce": nonce_from_the_client,
            "options": {
                "submit_for_settlement": True
            }
        })
        print(result)
        return HttpResponse('Ok')


    def payment_method_createview(request):
        eventlog('BRAINTREE - payment_method_createview')
        if request.method == "POST" and request.is_ajax():
            eventlog(request.POST)
            billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
            if not billing_profile:
                return HttpResponse({"message": "Cannot find this user"}, status_code=401)
            token = request.POST.get("token")
            if token is not None:
                new_card_obj = Card.objects.add_new(billing_profile, token)
                eventlog(new_card_obj) # this is where we start saving our cards too!

            return JsonResponse({"message": "Success your card was added !!"})
        return HttpResponse("error", status_code=401)

