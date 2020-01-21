from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
from stringkeeper.standalone_tools import *
from django.utils.http import is_safe_url
from .models import BillingProfile, Card
from orders.models import Order, SubscriptionPurchase
from carts.models import Cart
from .forms import PaymentMethodForm
from django.views.decorators.csrf import csrf_exempt

import braintree
from .extras import generate_order_id, transact, generate_client_token

BRAINTREE_PRODUCTION = getattr(settings, 'BRAINTREE_PRODUCTION', False)
BRAINTREE_MERCHANT_ID = getattr(settings, 'BRAINTREE_MERCHANT_ID', 's7s9hk3y2frmyq6n')
BRAINTREE_PUBLIC_KEY = getattr(settings, 'BRAINTREE_PUBLIC_KEY', 'hnzpmswf3hqpzwtj')
BRAINTREE_PRIVATE_KEY = getattr(settings, 'BRAINTREE_PRIVATE_KEY', '888ebe7f91701688efdc1f9c52471b8f')
BRAINTREE_BILLING_SERVICE = getattr(settings, 'BRAINTREE_BILLING_SERVICE', False)


def get_braintree_customer(request):
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

    eventlog('user first name: ' + request.user.first_name)
    eventlog('user last name: ' + request.user.last_name)
    eventlog('user email: ' + request.user.email)

    # == We grab the data about the billing profile from stringkeeper server
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)


    # === Here we make sure that the customer ID matches braintree records
    # === if it does not, we attempt to locate the user and update our records or create a new customer
    customer = None
    if billing_profile.braintree_customer_id == None:
        eventlog("customer email was NOT found on braintree server!")
        eventlog("Creating customer: ")
        
        result = gateway.customer.create({
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email
        })

        if result.is_success:
            eventlog('billing_profile.braintree_customer_id created.')
            billing_profile.braintree_customer_id = result.customer.id
            eventlog('billing_profile.braintree_customer_id changed from: ' + str(billing_profile.braintree_customer_id))
            eventlog('to: ' + str(billing_profile.braintree_customer_id))
            billing_profile.save(update_fields=["braintree_customer_id"])
            customer = gateway.customer.find(billing_profile.braintree_customer_id)
    
    if billing_profile.braintree_customer_id != None:
        eventlog("stringkeeper billing_profile.braintree_customer_id exists: " + str(billing_profile.braintree_customer_id))
        found_customer_id = None
        try:
            customer = gateway.customer.find(billing_profile.braintree_customer_id)
            found_customer_id = customer.id
            eventlog(str(found_customer_id))
        except:
            found_customer_id = None


        if found_customer_id != None:
            eventlog("customer id was found on braintree server.")
        else:
            eventlog("customer id was not found on braintree server - setting it to None: ")
            billing_profile.braintree_customer_id = None      

            eventlog('billing_profile.braintree_customer_id is None, searching by email')
            customer_email = None
            try:
                customer = gateway.customer.find(request.user.email)
                customer_email = customer.email
            except:
                pass

            if customer_email != None:
                eventlog(str(customer.email))
                eventlog("customer email was found on braintree server.")
                eventlog("Found customer by email -- updating customer ID to match braintree records: ")
                billing_profile.braintree_customer_id = customer.id
                eventlog("customer ID: " + str(billing_profile.braintree_customer_id))
                billing_profile.save(update_fields=["braintree_customer_id"])
            else:
                eventlog("customer email was NOT found on braintree server!")
                eventlog("Creating customer: ")
                
                result = gateway.customer.create({
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "email": request.user.email
                })

                if result.is_success:
                    search_results = gateway.customer.search(
                        braintree.CustomerSearch.email == request.user.email,
                    )
                    search_result_id = ''
                    for search_result in search_results:
                        eventlog('search_result: ' + str(search_result))
                        eventlog('billing_profile.braintree_customer_id created: ' + str(search_result.id))
                        eventlog('billing_profile.braintree_customer_id: ' + str(billing_profile.braintree_customer_id))
                        search_result_id = search_result.id

                    eventlog('billing_profile.braintree_customer_id: ' + str(billing_profile.braintree_customer_id))
                    billing_profile.braintree_customer_id = search_result_id
                    billing_profile.braintree_subscriptions = ['None']
                    eventlog('billing_profile.braintree_customer_id: ' + str(billing_profile.braintree_customer_id))
                    billing_profile.save()                    
                    # exit()

                    eventlog('billing_profile.braintree_customer_id changed to: ' + str(billing_profile.braintree_customer_id))
                     
                    
                    customer = gateway.customer.find(billing_profile.braintree_customer_id)
    
    return customer


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


eventlog('BRAINTREE BILLING SERVICE IS ACTIVE')
def payment_method_view(request):

    # === we prime our braintree server gateway here
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            environment=settings.BRAINTREE_ENVIRONMENT,
            merchant_id=settings.BRAINTREE_MERCHANT_ID,
            public_key=settings.BRAINTREE_PUBLIC_KEY,
            private_key=settings.BRAINTREE_PRIVATE_KEY
        )
    )
    # get customer
    customer = get_braintree_customer(request)
    
    # get billing profile
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    eventlog('braintree_customer first_name: ' + str(customer.first_name))
    braintree_customer_first_name = str(customer.first_name)
    eventlog('braintree_customer last_name: ' + str(customer.last_name))
    braintree_customer_last_name = str(customer.last_name)
    eventlog('braintree_customer email: ' + str(customer.email))
    braintree_customer_email = str(customer.email)

    eventlog('braintree_customer_first_name: ' + braintree_customer_first_name)        
    eventlog('braintree_customer_last_name: ' + braintree_customer_last_name)
    eventlog('braintree_customer_email: ' + braintree_customer_email)



    # PROCESS AJAX STUFF
    if request.is_ajax():
        eventlog('REQUEST IS AJAX')
        eventlog('request.POST: ' + str(request.POST))

        # detected removed subscription
        if 'subscriptionPurchase_order_id' in request.POST:
            data = request.POST['subscriptionPurchase_order_id']
            my_subscriptions, subscriptionPurchases = SubscriptionPurchase.objects.subscriptions_by_request_and_billing_profile(request, billing_profile)
            subscription_purchase = None
            for subPurchase in subscriptionPurchases:
                if str(subPurchase.order_id) == str(data):
                    subscription_purchase = subPurchase

            first_billing_date = subscription_purchase.is_canceled_final_date

            # braintree_subscription = gateway.subscription.find(subscription_purchase.)
            # update canceled subscription
            #create subscriptions with braintree payment token
            result = gateway.subscription.create({
                "payment_method_token": billing_profile.braintree_payment_method_token,
                "plan_id": subscription_purchase.subscription.slug,
                'first_billing_date': first_billing_date
            })
            eventlog('subscription: ' + str(subscription_purchase.subscription.slug) + ' success =  ' + str(result.is_success))
            debug_result(result)

            if result.is_success:
                subscription_purchase.is_canceled = False
                subscription_purchase.is_canceled_final_date = None
                subscription_purchase.is_canceled_initial_date = None
                subscription_purchase.braintree_customer_id = result.subscription.id
                subscription_purchase.save()

            url = request.META['HTTP_REFERER']
            eventlog("request.META['HTTP_REFERER'] : " + str(url))
            return JsonResponse({'href': str(url)})



        # detected removed subscription
        if 'removeSubscription' in request.POST:
            data = request.POST['removeSubscription']
            eventlog('RemoveSubscription: ' + str(data))
            braintree_subscription = gateway.subscription.find(data)
            slug_to_delete = braintree_subscription.plan_id
            #tell braintree to cancel
            result = gateway.subscription.cancel(str(data))
            

            my_subscriptions, subscriptionPurchases = SubscriptionPurchase.objects.subscriptions_by_request_and_billing_profile(request, billing_profile)
            eventlog('my_subscriptions: ' + str(my_subscriptions))
            eventlog('my_subscription_purchases: ' + str(subscriptionPurchases))

            #then we need to find the relationship between the subscription and the subscription purpose
            for subscriptionPurchase in subscriptionPurchases:
                eventlog('looking for ' + str(slug_to_delete) + ' in subscriptionPurchase subscription slug: ' + str(subscriptionPurchase.subscription.slug))
                if str(subscriptionPurchase.subscription.slug) == str(slug_to_delete):
                    eventlog('setting subscriptionPurchase.subscription.slug is_canceled to true.')
                    subscriptionPurchase.is_canceled = True
                    subscriptionPurchase.braintree_subscription_id = braintree_subscription.id
                    subscriptionPurchase.is_canceled_initial_date = timezone.now()
                    subscriptionPurchase.is_canceled_final_date = braintree_subscription.next_billing_date
                    subscriptionPurchase.save()
            url = request.META['HTTP_REFERER']
            eventlog("request.META['HTTP_REFERER'] : " + str(url))
            return JsonResponse({'href': str(url)})



    # Remove any extra credit cards, consilidate into one card.
    eventlog('len(customer.credit_cards): ' + str(len(customer.credit_cards)))
    if len(customer.credit_cards) > 0:
        # we need to transfer subscriptions on credit card 1 to credit card 0
        for i in range(0, len(customer.credit_cards)):
            customer_subscriptions = customer.credit_cards[i].subscriptions
            for subscription in customer_subscriptions:
                result = gateway.subscription.update(subscription.id, {
                    # "id": "new_id",
                    "payment_method_token": customer.credit_cards[0].token,
                    # "price": "14.00",
                    # "plan_id": "new_plan",
                    # "merchant_account_id": "new_merchant_account"
                })

        for i in range(1, len(customer.credit_cards)):
            result = gateway.payment_method.delete(customer.credit_cards[i].token)

    # get list of customer subscriptions given the one new payment card.
    customer_subscriptions = []
    try:
        customer_subscriptions = customer.credit_cards[0].subscriptions
    except:
        pass
    customer_active_subscriptions = []
    active_subscription = False
    if len(customer_subscriptions) > 0:
        for subscription in customer_subscriptions:
            eventlog('SUBCRIPTION id: ' + str(subscription.id) + ' for ' + str(customer.credit_cards[0].token))
            if subscription.status == 'Active' or subscription.status == 'Pending':
                active_subscription = True
                customer_active_subscriptions.append(subscription)
    


    

    # # == We grab the data about the cart from stringkeeper
    # cart, cart_created = Cart.objects.new_or_get(request)
    # eventlog('cart: ' + str(cart))
    # eventlog('cart_created: ' + str(cart_created))

    # == We grab the data about the order from stringkeeper
    # order_profile, order_profile_created = Order.objects.new_or_get(billing_profile, cart)
    # eventlog('order_profile: ' + str(order_profile))
    # order_billing_address = order_profile.billing_address
    # eventlog('order_billing_address: ' + str(order_billing_address))
    # eventlog('order_profile_created: ' + str(order_profile_created))

    if not billing_profile:
        return redirect("/cart")

    next_url = None
    next_ = request.GET.get('next')
    if is_safe_url(next_, request.get_host()):
        next_url = next_

    client_token = gateway.client_token.generate({
        "customer_id": billing_profile.braintree_customer_id
    })
    eventlog('client_token: ' + str(client_token))
    
    payment_method_nonce = ''
    success_token = ''

    # we setup the payment form with known data for customer to review
    paymentform = PaymentMethodForm( request.POST or None, initial={
            'first_name': billing_profile.first_name,
            'last_name': billing_profile.last_name,
            'street': billing_profile.street,
            'postal_code': billing_profile.postal_code
            
            })
    # form.fields["first_name"] = request.user.first_name 

    # testvariable = 'nonce before post'
    nonce = 'nonce before post'
    # gordon = 'gordon before post'


    customer_canceled_subscriptionPurchases = []

    my_subscriptions, subscriptionPurchases = SubscriptionPurchase.objects.subscriptions_by_request_and_billing_profile(request, billing_profile)
    
    # make a list of canceled subscriptions
    for subscriptionPurchase in subscriptionPurchases:
        if subscriptionPurchase.is_canceled == True:
            customer_canceled_subscriptionPurchases.append(subscriptionPurchase)

        #also -- if the stringkeeper braintree subscription ID in the subscriptionPurchase object 
        # does not match the braintree subscription id -- set the id accordingly.        
        subscription_slug = subscriptionPurchase.subscription.slug
        eventlog('Checking subscriptionPurchase.subscription.slug: ' + str(subscription_slug))
        for customer_subscription in customer_subscriptions:
            if str(subscription_slug) == str(customer_subscription.plan_id):
                eventlog('customer_subscription.plan_id: ' + str(customer_subscription.plan_id))
                eventlog('subscription_slug: ' + str(subscription_slug))
                eventlog('customer_subscription.id: ' + str(customer_subscription.id))
                eventlog('subscriptionPurchase.braintree_subscription_id: ' + str(subscriptionPurchase.braintree_subscription_id))
                eventlog('SUBSCRIPTION_SLUG: ' + str(subscription_slug) + ' MATCHES ' + str(customer_subscription.plan_id))
                if str(subscriptionPurchase.braintree_subscription_id) != str(customer_subscription.id):
                    eventlog('subscriptionPurchase.braintree_subscription_id: ' + str(subscriptionPurchase.braintree_subscription_id) + ' DOES NOT MATCH ' + str(customer_subscription.id))
                    subscriptionPurchase.braintree_subscription_id = str(customer_subscription.id)
                    subscriptionPurchase.save()

    # PROCESS THE BRAINTREE DROPIN
    if request.method == 'POST' and request.is_ajax() == False:
        eventlog('REQUEST IS POST AND NOT AJAX')
        eventlog('request.POST: ' + str(request.POST))

        nonce = str(request.POST.get('nonce'))
        eventlog('nonce: ' + str(nonce))

        # testvariable = request.POST.get('testvariable')
        # eventlog('testvariable: ' + str(testvariable))

        # gordon = request.POST.get('gordon')
        # eventlog('gordon: ' + str(gordon))

        customer = gateway.customer.find(billing_profile.braintree_customer_id)
        eventlog("UPDATING CUSTOMER")
        eventlog("len(customer.credit_cards): " + str(len(customer.credit_cards)))
        billing_profile.braintree_payment_method_token = customer.credit_cards[0].token
        billing_profile.save(update_fields=["braintree_payment_method_token"])
        result = gateway.customer.update(billing_profile.braintree_customer_id, {
            "payment_method_nonce": nonce,
            "email": request.user.email,
            "credit_card": {
                "options": {
                    "make_default": True,
                    "update_existing_token": billing_profile.braintree_payment_method_token,
                },
            }
        })
        debug_result(result)

    new_billing_profile_subscriptions_array = []
    for braintree_subscription in customer_active_subscriptions:
        eventlog('CHECKING BILLING FOR ACTIVE SUBSCRIPTION: ' + str(braintree_subscription.id))
        searching = True
        found_match = False
        while searching == True:
            for billing_subscription in billing_profile.braintree_subscriptions:
                if str(billing_subscription) == str(braintree_subscription.id):
                    eventlog('BILLING ACTIVE SUBSCRIPTION MATCH ' + str(billing_subscription))
                    new_billing_profile_subscriptions_array.append(braintree_subscription.id)
                    found_match = True
                    searching = False
            searching = False
        eventlog('found match = ' + str(found_match))
        if found_match == False:
            eventlog('Adding ' + str(braintree_subscription.id) + ' to billing braintree_subscriptions.' )
            new_billing_profile_subscriptions_array.append(braintree_subscription.id)
    
    for i in range(0, len(billing_profile.braintree_subscriptions)):
        billing_profile.braintree_subscriptions[i] = None
        billing_profile.save(update_fields=["braintree_subscriptions"])

    eventlog('len(billing_profile.braintree_subscriptions): ' + str(len(billing_profile.braintree_subscriptions)))
    eventlog('len(new_billing_profile_subscriptions_array): ' + str(len(new_billing_profile_subscriptions_array)))
    for i in range(0, len(new_billing_profile_subscriptions_array)):
        try:
            billing_profile.braintree_subscriptions[i] = new_billing_profile_subscriptions_array[i]
            billing_profile.save(update_fields=["braintree_subscriptions"])
        except:
            billing_profile.braintree_subscriptions.append(new_billing_profile_subscriptions_array[i])
            billing_profile.save(update_fields=["braintree_subscriptions"])


    context = {
        # 'gordon': gordon,
        # 'testvariable': testvariable,
        'nonce': nonce,
        'paymentform': paymentform,
        'braintree_payment_method_token': billing_profile.braintree_payment_method_token,
        'customer_active_subscriptions': customer_active_subscriptions,
        'customer_canceled_subscriptionPurchases': customer_canceled_subscriptionPurchases,
        
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,

        'billing_profile': str(billing_profile),
        'billing_profile_created': str(billing_profile_created),
        'billing_profile.first_name': str(billing_profile.first_name),
        'billing_profile.last_name': str(billing_profile.last_name),
        'billing_profile.street': str(billing_profile.street),
        'billing_profile.postal_code': str(billing_profile.postal_code),
        'braintree_customer_id': str(billing_profile.braintree_customer_id),


        'braintree_customer_first_name': braintree_customer_first_name,
        'braintree_customer_last_name': braintree_customer_last_name,
        'braintree_customer_email': braintree_customer_email,

        # 'cart': str(cart),
        # 'cart_created': str(cart_created),

        # 'order_profile': str(order_profile),
        # 'order_profile_created': str(order_profile_created), 
        # 'order_billing_address': str(order_billing_address),   


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

