from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
from stringkeeper.standalone_tools import *
from django.utils.http import is_safe_url
from .models import BillingProfile, Card

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

        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

        if not billing_profile:
            return redirect("/cart")

        next_url = None
        next_ = request.GET.get('next')
        if is_safe_url(next_, request.get_host()):
            next_url = next_


        context = {
            'ascii_art': get_ascii_art()
            }
        eventlog(' ABOUT TO HIT LINE 94 ')
        return render(request, 'billing/payment-method.html', {})


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

