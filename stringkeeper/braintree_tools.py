

import braintree
from stringkeeper.standalone_tools import *

from billing.models import BillingProfile

from django.conf import settings

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
            if customer.first_name != request.user.first_name:
                result = gateway.customer.update(found_customer_id, {
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name
                })
            elif customer.last_name != request.user.last_name:
                result = gateway.customer.update(found_customer_id, {
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name
                })
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
