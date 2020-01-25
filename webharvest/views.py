from django.shortcuts import render
from stringkeeper.standalone_tools import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView
from billing.models import BillingProfile
from orders.models import Order, SubscriptionPurchase
# Create your views here.
from .mixins import CsrfExemptMixin
from django.http import HttpResponse
import json

#LoginRequiredMixin,
class WebHarvestHomeView(DetailView):
    template_name = 'webharvest/home.html'

    def get_context_data(self, *args, **kwargs):
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(self.request)
        my_subscriptions, subscription_purchases, live_subscription_purchases = SubscriptionPurchase.objects.subscriptions_by_request_and_billing_profile(self.request, billing_profile)

        context = super(WebHarvestHomeView, self).get_context_data(*args, **kwargs)
        context['ascii_art'] = get_ascii_art()
        context['billing_profile'] = billing_profile
        context['subscription_purchases'] = subscription_purchases
        context['my_subscriptions'] = my_subscriptions
        context['live_subscription_purchases'] = live_subscription_purchases
        subscribed = False
        for live_subscription_purchase in live_subscription_purchases:
            if str(live_subscription_purchase.subscription.slug) == 'web-harvest':
                subscribed = True
        context['subscribed'] = subscribed
        title = ''
        if not subscribed:
            title = 'Web Harvest Demo'

        context['title'] = title

        return context

    def get_object(self):
        return self.request.user


class WebHarvestWebhookView(CsrfExemptMixin, View): # HTTP GET -- def get() CSRF?????
    def get(self, request, *args, **kwargs):
        return HttpResponse("Thank you", status=200)

    def post(self, request, *args, **kwargs):

        eventlog('WebHarvestWebhookView POST request: ' + str(request))
        eventlog('WebHarvestWebhookView POST args: ' + str(*args))
        eventlog('WebHarvestWebhookView POST kwargs: ' + str(**kwargs))
        data = request.POST
        eventlog('WebHarvestWebhookView POST data: ' + str(data))
        json.dumps(data)
        eventlog('WebHarvestWebhookView POST json.dumps(data): ' + str(data))
        # t_id = request.POST.json['id']
        # eventlog('WebHarvestWebhookView POST t_id: ' + str(t_id))
        # t_name = request.POST.json['name']
        # eventlog('WebHarvestWebhookView POST t_name: ' + str(t_name))
        # created_on = request.POST.json['created_on']
        # eventlog('WebHarvestWebhookView POST created_on: ' + str(created_on))
        # modified_on = request.POST.json['modified_on']
        # eventlog('WebHarvestWebhookView POST modified_on: ' + str(modified_on))
        # desc = request.POST.json['desc']
        # eventlog('WebHarvestWebhookView POST desc: ' + str(desc))

        return HttpResponse("Thank you", status=200)

