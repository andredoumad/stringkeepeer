from django.conf import settings
import random
import string
from datetime import date
import datetime
import braintree
from orders.models import Order
from stringkeeper.standalone_tools import *

def generate_order_id():
    date_str = date.today().strftime('%Y%m%d')[2:] + str(datetime.datetime.now().second)
    rand_str = "".join([random.choice(string.digits) for count in range(3)])
    return date_str + rand_str

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        environment=settings.BRAINTREE_ENVIRONMENT,
        merchant_id=settings.BRAINTREE_MERCHANT_ID,
        public_key=settings.BRAINTREE_PUBLIC_KEY,
        private_key=settings.BRAINTREE_PRIVATE_KEY
    )
)

# Generate a client token https://developers.braintreepayments.com/start/hello-server/python
def generate_client_token():
    eventlog('BRAINTREE_ENVIRONMENT: ' + str(settings.BRAINTREE_ENVIRONMENT))
    eventlog('BRAINTREE_MERCHANT_ID: ' + str(settings.BRAINTREE_MERCHANT_ID))
    eventlog('BRAINTREE_PUBLIC_KEY: ' + str(settings.BRAINTREE_PUBLIC_KEY))
    eventlog('BRAINTREE_PRIVATE_KEY: ' + str(settings.BRAINTREE_PRIVATE_KEY))
    client_token = gateway.client_token.generate()
    
    eventlog('client_token: ' + str(client_token))
    return gateway.client_token.generate()


# Create a transaction https://developers.braintreepayments.com/start/hello-server/python
def transact(options):
    return gateway.transaction.sale(options)

def find_transaction(id):
    return gateway.transaction.find(id)
