from django.contrib import admin

# Register your models here.
from .models import Subscription

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug']
    class Meta:
        model = Subscription


admin.site.register(Subscription)