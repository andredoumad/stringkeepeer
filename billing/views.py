from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
from stringkeeper.standalone_tools import *
from django.utils.http import is_safe_url
from .models import BillingProfile, Card

# _STRIPE_
import stripe

STRIPE_BILLING_SERVICE = getattr(settings, 'STRIPE_BILLING_SERVICE', False)
PAYPAL_BILLING_SERVICE= getattr(settings, 'PAYPAL_BILLING_SERVICE', False)

STRIPE_PUB_KEY = 'pk_test_k8LAxPXmWxonT6ZUDVxjsuzL00LCGJ2rLX'
stripe.api_key = 'sk_test_UQ6hFgP5OZ9KXeSWvO39jgTb0099ffMFNJ'

if STRIPE_BILLING_SERVICE:

    def payment_method_view(request):
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
            'payment_company': 'stripe'
            }

        return render(request, 'billing/payment-method.html', context)


    def payment_method_createview(request):
        if request.method == "POST" and request.is_ajax():
            eventlog(request.POST)
            billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

            if not billing_profile:
                return HttpResponse({"message": "Cannot find this user"}, status_code=401)
            # print(request.POST)
            token = request.POST.get("token")
            if token is not None:
                customer = stripe.Customer.retrieve(billing_profile.stripe_customer_id)
                # https://stripe.com/docs/api/customers/object?lang=python
                card_response = customer.sources.create(source=token)
                new_card_obj = Card.objects.add_new(billing_profile, card_response)
                eventlog(new_card_obj) # this is where we start saving our cards too!

            return JsonResponse({"message": "Success your card was added !!"})
        return HttpResponse("error", status_code=401)




if PAYPAL_BILLING_SERVICE:

    def payment_method_view(request):
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
            'payment_company': 'paypal',
            'testThing': 'testing123 from context view'
            }

        return render(request, 'billing/payment-method.html', context)


    def payment_method_createview(request):
        if request.method == "POST" and request.is_ajax():
            eventlog(request.POST)
            billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

            if not billing_profile:
                return HttpResponse({"message": "Cannot find this user"}, status_code=401)
            # print(request.POST)
            token = request.POST.get("token")
            if token is not None:
                # customer = stripe.Customer.retrieve(billing_profile.stripe_customer_id)
                # # https://stripe.com/docs/api/customers/object?lang=python
                # card_response = customer.sources.create(source=token)
                # new_card_obj = Card.objects.add_new(billing_profile, card_response)
                new_card_obj = Card.objects.add_new(billing_profile, token)
                eventlog(new_card_obj) # this is where we start saving our cards too!

            return JsonResponse({"message": "Success your card was added !!"})
        return HttpResponse("error", status_code=401)