from django.shortcuts import render
from stringkeeper.standalone_tools import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView, ListView
from billing.models import BillingProfile
from orders.models import Order, SubscriptionPurchase
from rest_framework.test import APIRequestFactory
# Create your views here.
from .mixins import CsrfExemptMixin
from django.http import HttpResponse, Http404, HttpResponseForbidden
import json, requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings

from .forms import ComposeForm
from django.views.generic.edit import FormMixin
from .models import WebharvestThread, WebharvestChatMessage


BASE_URL = getattr(settings, 'BASE_URL', False)

# OLD CORE SYSTEM
#LoginRequiredMixin,
class WebHarvestHomeView(DetailView):
    template_name = 'webharvest/home.html'


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('register')
        return super(WebHarvestHomeView, self).dispatch(request, *args, **kwargs)

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

        context['authenticated'] = self.request.user.is_authenticated
        if not subscribed:
            title = 'Web Harvest Demo'

        context['title'] = title

        return context

    def get_object(self):
        return self.request.user






# NEW WEBHARVEST CONSUMERS 
class InboxView(LoginRequiredMixin, ListView):
    template_name = 'webharvest/inbox.html'
    def get_queryset(self):
        return WebharvestThread.objects.by_user(self.request.user)


class ThreadView(LoginRequiredMixin, FormMixin, DetailView):
    template_name = 'webharvest/thread.html'
    form_class = ComposeForm
    success_url = './'

    def get_queryset(self):
        return WebharvestThread.objects.by_user(self.request.user)

    def get_object(self):
        other_username  = self.kwargs.get("username")
        eventlog('get_object other_username: ' + str(other_username))

        eventlog('self.request.user: ' + str(self.request.user))
        obj, created    = WebharvestThread.objects.get_or_new(self.request.user, other_username)
        if obj == None:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        thread = self.get_object()
        user = self.request.user
        eventlog('form_valid user: ' + str(user))
        message = form.cleaned_data.get("message")
        WebharvestChatMessage.objects.create(user=user, thread=thread, message=message)
        return super().form_valid(form)









class WebHarvestWebhookView(CsrfExemptMixin, View): # HTTP GET -- def get() CSRF?????
    def get(self, request, *args, **kwargs):
        eventlog('WebHarvestWebhookView GET request: ' + str(request))
        eventlog('WebHarvestWebhookView GET args: ' + str(*args))
        eventlog('WebHarvestWebhookView GET kwargs: ' + str(**kwargs))
        data = request.GET
        eventlog('WebHarvestWebhookView GET data: ' + str(data))
        json.dumps(data)
        eventlog('WebHarvestWebhookView GET json.dumps(data): ' + str(data))
        return HttpResponse("", status=200)

    def post(self, request, *args, **kwargs):

        eventlog('WebHarvestWebhookView POST request: ' + str(request))
        eventlog('WebHarvestWebhookView POST args: ' + str(*args))
        eventlog('WebHarvestWebhookView POST kwargs: ' + str(**kwargs))
        data = request.POST
        eventlog('WebHarvestWebhookView POST data: ' + str(data))
        json.dumps(data)
        eventlog('WebHarvestWebhookView POST json.dumps(data): ' + str(data))
        # return HttpResponse("", status=200)
        if 'user' in data:
            eventlog('user: ' + str(data['user']))            

        if 'chat_message' in data:
            eventlog('chat_message: ' + str(data['chat_message']))
            # factory = APIRequestFactory()
            # request = factory.post('/notes/', {'title': 'new idea'})
            # eventlog('request: ' + str(request))

            user = data['user']
            payload = {
                'recipient': user,
                'body': data['chat_message']
            }
            requests.post(str(BASE_URL + '/webharvest/api/v1/message/'), payload)

        response = {
            'user': 'andre@blackmesanetwork.com',
            'chat': 'the record of chat for user'
        }
        return JsonResponse(response)

