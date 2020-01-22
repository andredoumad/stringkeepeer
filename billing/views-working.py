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

        # === we prime our braintree server gateway here
        gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                environment=settings.BRAINTREE_ENVIRONMENT,
                merchant_id=settings.BRAINTREE_MERCHANT_ID,
                public_key=settings.BRAINTREE_PUBLIC_KEY,
                private_key=settings.BRAINTREE_PRIVATE_KEY
            )
        )

        # == We grab the data about the user profile from stringkeeper server
        user_first_name = str(request.user.first_name)
        user_last_name = str(request.user.last_name)
        user_email = str(request.user.email)
        eventlog('user first name: ' + user_first_name)
        eventlog('user last name: ' + user_last_name)
        eventlog('user email: ' + user_email)

        # == We grab the data about the billing profile from stringkeeper server
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

        braintree_payment_method_token = billing_profile.braintree_payment_method_token
        eventlog('braintree_payment_method_token: ' + str(braintree_payment_method_token))

        # === Here we make sure that the customer ID matches braintree records
        # === if it does not, we attempt to locate the user and update our records or create a new customer
        if braintree_customer_id != None:
            eventlog("stringkeeper braintree_customer_id exists: " + str(braintree_customer_id))
            collection = gateway.customer.search(
                braintree.CustomerSearch.id == braintree_customer_id 
            )

            found_customer_id = None 
            for customer in collection.items:
                found_customer_id = customer.id
                eventlog(str(customer.id))
    
            if found_customer_id != None:
                eventlog("customer id was found on braintree server.")
            else:
                eventlog("customer id was not found on braintree server - setting it to None: ")
                braintree_customer_id = None      

                eventlog('braintree_customer_id is None, searching by email')

                collection = gateway.customer.search(
                    braintree.CustomerSearch.email == "john.doe@example.com",
                )

                customer_email = None 
                for customer in collection.items:
                    customer_email = customer.email

                if customer_email != None:
                    eventlog(str(customer.email))
                    eventlog("customer email was found on braintree server.")
                    eventlog("Found customer by email -- updating customer ID to match braintree records: ")
                    braintree_customer_id = customer.id
                    eventlog("customer ID: " + str(braintree_customer_id))
                    billing_profile.braintree_customer_id = customer_id
                    billing_profile.save(update_fields=["braintree_customer_id"])
                else:
                    eventlog("customer email was NOT found on braintree server!")
                    eventlog("Creating customer: ")
                    
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

        # == We grab the data about the customer from braintree servers
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


        # == We grab the data about the cart from stringkeeper
        cart, cart_created = Cart.objects.new_or_get(request)
        eventlog('cart: ' + str(cart))
        eventlog('cart_created: ' + str(cart_created))

        # == We grab the data about the order from stringkeeper
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
        success_token = ''

        # we setup the payment form with known data for customer to review
        paymentform = PaymentMethodForm( request.POST or None, initial={
                'first_name': billing_profile_first_name,
                'last_name': billing_profile_last_name,
                'street': billing_profile_street,
                'postal_code': billing_profile_postal_code
                
                })
        # form.fields["first_name"] = user_first_name 

        testvariable = 'nonce before post'
        nonce = 'nonce before post'
        gordon = 'gordon before post'
        if request.method == 'POST':

            eventlog('request.method: ' + str(request.method))

            # === we take the data from the fields and update our billing profile
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
                    "postal_code",
                    ])
            
            # result = gateway.payment_method_nonce.create("A_PAYMENT_METHOD_TOKEN")
            # nonce = result.payment_method_nonce.nonce
            
            # result = gateway.customer.update(braintree_customer_id, {
            #     "payment_method_nonce": payment_method_nonce,
            #     "email": request.user.email,
            #     # fake credit card 4012000077777777
            #     # another fake 4111111111111111
            #     "credit_card": {
            #         "options": {
            #             "update_existing_token": client_token,
            #         },
            #         "billing_address": {
            #             "street_address": billing_profile.street,
            #             "postal_code": billing_profile.postal_code,
            #             "options": {
            #                 "update_existing": True
            #             }
            #         }
            #     }
            # })
            nonce = str(request.POST.get('nonce'))
            eventlog('nonce: ' + str(nonce))

            # eventlog('result: ' + str(result))

            testvariable = request.POST.get('testvariable')
            eventlog('testvariable: ' + str(testvariable))

            gordon = request.POST.get('gordon')
            eventlog('gordon: ' + str(gordon))


            def debug_result(result):
                eventlog('result.is_success: ' + str(result.is_success))
                try:
                    for error in result.errors.deep_errors:
                        eventlog(error.attribute)
                        eventlog(error.code)
                        eventlog(error.message)
                except:
                    pass

                try:
                    for error in result.errors.for_object("customer"):
                        peventlogrint(error.attribute)
                        eventlog(error.code)
                        eventlog(error.message)
                except:
                    pass

                try:
                    for error in result.errors.for_object("customer").for_object("credit_card"):
                        eventlog(error.attribute)
                        eventlog(error.code)
                        eventlog(error.message)
                except:
                    pass
                
                try:
                    eventlog(result.token)
                except:
                    pass

                try:
                    eventlog(result.params)
                except:
                    pass

                # try:
                #     eventlog('result.customer.payment_methods[0].token: ' + result.customer.payment_methods[0].token)
                # except:
                #     pass

            # result = gateway.payment_method.create({
            #     "customer_id": braintree_customer_id,
            #     "payment_method_nonce": nonce,
            #     "options": {
            #     "make_default": True,
            #     "fail_on_duplicate_payment_method": True

            #     }
            # })



            customer = gateway.customer.find(braintree_customer_id)
            eventlog("UPDATING CUSTOMER")
            eventlog("len(customer.credit_cards): " + str(len(customer.credit_cards)))
            braintree_payment_method_token = customer.credit_cards[0].token
            billing_profile.braintree_payment_method_token = braintree_payment_method_token
            billing_profile.save(update_fields=["braintree_payment_method_token"])
            eventlog("PAYMENT METHOD TOKEN: " + braintree_payment_method_token)
            result = gateway.customer.update(braintree_customer_id, {
                "payment_method_nonce": nonce,
                "email": user_email,
                "credit_card": {
                    "options": {
                        "update_existing_token": braintree_payment_method_token,
                    },
                    "billing_address": {
                        "street_address": billing_profile_street,
                        "postal_code": billing_profile_postal_code,
                        "options": {
                            "update_existing": True
                        }
                    }
                }
            })
            debug_result(result)

            eventlog('CREATING SUBSCRIPTION! ')
            result = gateway.subscription.create({
                "payment_method_token": braintree_payment_method_token,
                "plan_id": "data-mining"
            })

            # result = gateway.transaction.sale({
            #     "amount": "10.00",
            #     "customer_id": braintree_customer_id,
            #     "options": {
            #         "submit_for_settlement": True
            #     }
            # })
            # debug_result(result)
            
            # transaction = result.transaction
            # eventlog('transaction.status: ' + str(transaction.status))



        context = {
            'gordon': gordon,
            'testvariable': testvariable,
            'nonce': nonce,
            'paymentform': paymentform,
            'braintree_payment_method_token': braintree_payment_method_token,
            
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
        eventlog(result)
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

