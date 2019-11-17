from django.urls import path, re_path #url
from carts.views import (
    cart_home
)

app_name = 'carts'
urlpatterns = [
    path('', cart_home, name='home')
]
