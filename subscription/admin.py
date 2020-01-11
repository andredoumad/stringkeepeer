from django.contrib import admin

from .models import Subscription, SubscriptionFile


class SubscriptionFileInline(admin.TabularInline):
    model = SubscriptionFile
    extra = 1


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug', 'is_digital']
    inlines = [SubscriptionFileInline]
    class Meta:
        model = Subscription

admin.site.register(Subscription, SubscriptionAdmin)