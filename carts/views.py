from django.shortcuts import render
from stringkeeper.standalone_logging import *
# Create your views here.

def cart_home(request):
    cart_id = request.session.get('cart_id', None)
    if cart_id is None: #and isinstance(cart_id, int):
        eventlog('get new cart')
        request.session['cart_id']      = 12 #Set
    else:
        eventlog('Cart ID exists')

    # print(request.session) # on the request
    # print(dir(request.session))
    # request.session.session_expiry(300) # 5 MINUTES
    # key = request.session.session_key
    # print(key)
    #request.session['first_name'] = 'Andre'
    # request.session['user']         = request.user.username

    return render(request, "carts/home.html", {})
