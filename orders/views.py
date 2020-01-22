from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.views.generic import View, ListView, DetailView
from django.shortcuts import render
from stringkeeper.standalone_tools import *
# Create your views here.

from billing.models import BillingProfile
from .models import Order, SubscriptionPurchase

class OrderListView(LoginRequiredMixin, ListView):

    def get_queryset(self):
        my_profile = BillingProfile.objects.new_or_get(self.request)
        return Order.objects.by_request(self.request)

class OrderDetailView(LoginRequiredMixin, DetailView):

    def get_object(self):
        # return Order.objects.get(id=self.kwargs.get('id'))
        # return Order.objects.get(slug=self.kwargs.get('slug'))
        qs = Order.objects.by_request(
            self.request
            ).filter(order_id = self.kwargs.get('order_id'))
        if qs.count() == 1:
            return qs.first()
        return Http404

class LibraryView(LoginRequiredMixin, ListView):
    template_name = 'orders/library.html'

    def get_context_data(self, *args, **kwargs):

        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(self.request)
        my_subscriptions, subscriptionPurchases = SubscriptionPurchase.objects.subscriptions_by_request_and_billing_profile(self.request, billing_profile)
        eventlog('billing_profile: ' + str(billing_profile))
        eventlog('subscriptionPurchases: ' + str(subscriptionPurchases))
        context = super(LibraryView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Update Email'
        context['ascii_art'] = get_ascii_art()
        context['subscriptionPurchases'] = subscriptionPurchases
        context['billing_profile'] = billing_profile
        context['testing'] = 'testing'
        return context

    def get_queryset(self):
        return SubscriptionPurchase.objects.subscriptions_by_request(self.request) #.by_request(self.request).digital()

class VerifyOwnership(View):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            data = request.GET 
            subscription_id = request.GET.get('subscription_id', None)
            if subscription_id is not None:
                subscription_id = int(subscription_id)
                ownership_ids = SubscriptionPurchase.objects.subscriptions_by_id(request)
                if subscription_id in ownership_ids:
                    return JsonResponse({'owner': True})
            return JsonResponse({'owner': False})
        raise Http404
