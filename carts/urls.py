from django.urls import path, re_path #url
from carts.views import (
    cart_home,
    cart_update,
    checkout_home
)

app_name = 'carts'
urlpatterns = [
    path('', cart_home, name='home'),
    path('checkout/', checkout_home, name='checkout'),
    path('update/', cart_update, name='update'),
]
