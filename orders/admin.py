from django.contrib import admin

from .models import Order, SubscriptionPurchase

admin.site.register(Order)

admin.site.register(SubscriptionPurchase)