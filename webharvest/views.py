from django.shortcuts import render
from stringkeeper.standalone_tools import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView, ListView
from billing.models import BillingProfile
from orders.models import Order, SubscriptionPurchase
from rest_framework.test import APIRequestFactory
from .mixins import CsrfExemptMixin
from django.http import HttpResponse, Http404, HttpResponseForbidden
import json, requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from .forms import ComposeForm, WebharvestJobForm
from django.views.generic.edit import FormMixin
from .models import WebharvestThread, WebharvestChatMessage, WebharvestJob
from webharvest.consumers import WebharvestConsumer
from .multiform import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
import string

User = get_user_model()

BASE_URL = getattr(settings, 'BASE_URL', False)

# OLD CORE SYSTEM
#LoginRequiredMixin,
class WebHarvestHomeView(DetailView):
    template_name = 'webharvest/home.html'


    def dispatch(self, request, *args, **kwargs):
        # if not request.user.is_authenticated:
        #     return redirect('register')
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


# class ThreadView(LoginRequiredMixin, FormMixin, DetailView):
class ThreadView(FormMixin, DetailView):
    template_name = 'webharvest/thread.html'
    form_class = ComposeForm
    second_form_class = WebharvestJobForm
    success_url = './'

    def __init__(self):
        self.bool_temp_user = False
        self.user_ip = None
        self.temp_user = None
        self.temp_user_first = ''
        self.temp_user_last = ''
        self.temp_user_password = ''
        self.temp_user_email = ''
        self.temp_user_full_name = ''
        self.temp_user_id = ''

    def ConvertUserIPToUserEmail(self):
        eventlog('CREATING TEMPORARY USER EMAIL!')
        d = dict(enumerate(string.ascii_lowercase, 1))
        eventlog(d[3]) # c

        eventlog('self.request....')
        eventlog('self.request: ' + str(self.request))
        self.user_ip = get_client_ip(self.request)
        eventlog('self.user_ip: ' + str(self.user_ip))
        ip_alphas = ''
        for item in self.user_ip:
            if item.isdigit():
                if int(item) == 0:
                    ip_alphas += str('Z')
                else:                    
                    eventlog('item: ' + str(item))
                    ip_alphas += str(d[int(item)])
            else:
                if item.isalpha():
                    ip_alphas += item
                else:
                    ip_alphas += 'A'
        ip_alphas = (ip_alphas[:26] + '..') if len(ip_alphas) > 26 else ip_alphas
        eventlog('ip_alphas = ' + str(ip_alphas))
        self.temp_user_first = ip_alphas
        self.temp_user_last = 'temporaryuser'
        self.temp_user_password = ip_alphas
        self.temp_user_email = str(str(ip_alphas) + '@stringkeeper.com') 
        eventlog('self.temp_user_email = ' + self.temp_user_email)

    def RegisterTemporaryUser(self):
        self.temp_full_name = str(str(self.temp_user_first) + ' ' + str(self.temp_user_last))
        self.temp_user_id = str(str(self.temp_user_first) + str(''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(15))) + str(self.temp_user_last))

        self.temp_user = User.objects.create_user(
            email = self.temp_user_email,
            password = self.temp_user_password,
            first_name = self.temp_user_first,
            last_name = self.temp_user_last,
            full_name = self.temp_full_name,
        )
        self.temp_user.bool_temporary_user = True
        self.temp_user.is_active = True
        self.temp_user.bool_webharvest_chat_active = True
        self.temp_user.temporary_user_ip = self.user_ip
        self.temp_user.user_id = self.temp_user_id

        self.UpdateUserGeoIPData(self.temp_user, self.user_ip)

    def UpdateUserGeoIPData(self, user, user_ip):
        try:
            geo_request_url = 'https://get.geojs.io/v1/ip/geo/' + str(user_ip) + '.json'
            geo_request = requests.get(geo_request_url)
            geo_data = geo_request.json()
            eventlog(geo_data)
            for key, value in geo_data.items():
                eventlog('item: ' + str(key) + ' : ' + str(value))
                if key == 'organization_name':
                    user.geo_ip_organization_name = str(value)
                elif key == 'region':
                    user.geo_ip_region = str(value)
                elif key == 'accuracy':
                    user.geo_ip_accuracy = str(value)
                elif key == 'organization':
                    user.geo_ip_organization = str(value)
                elif key == 'timezone':
                    user.geo_ip_timezone = str(value)
                elif key == 'longitude':
                    user.geo_ip_longitude = str(value)
                elif key == 'country_code3':
                    user.geo_ip_country_code3 = str(value)
                elif key == 'area_code':
                    user.geo_ip_area_code = str(value)
                elif key == 'ip':
                    user.geo_ip_ip = str(value)
                elif key == 'city':
                    user.geo_ip_city = str(value)
                elif key == 'country':
                    user.geo_ip_country = str(value)
                elif key == 'continent_code':
                    user.geo_ip_continent_code = str(value)
                elif key == 'country_code':
                    user.geo_ip_country_code = str(value)
                elif key == 'latitude':
                    user.geo_ip_latitude = str(value)
        except:
            pass
        user.save()

    def GetOrMakeTemporaryUser(self):
        self.bool_temp_user = True
        self.ConvertUserIPToUserEmail()
        user_qs = None
        user_qs = User.objects.filter(email=self.temp_user_email)
        searching = True
        the_user = None
        while searching:
            for user in user_qs:
                eventlog('user_qs user: ' + str(user))
                if len(str(user)) > 3:
                    the_user = user
                    searching = False
            searching = False

        eventlog('user: ' + str(the_user))
        if the_user == None:
            self.RegisterTemporaryUser()
        else:
            self.temp_user = the_user

    def get_queryset(self):
        return WebharvestThread.objects.by_user(self.request.user)

    def get_object(self):
        self.user_ip = get_client_ip(self.request)
        self.the_user = None
        if str(self.request.user) == 'AnonymousUser':
            eventlog('USER IS ANONYMOUS!!')
            self.GetOrMakeTemporaryUser()
            self.the_user = self.temp_user
        else:
            self.UpdateUserGeoIPData(self.request.user, self.user_ip)
            self.the_user = self.request.user

        other_username  = self.kwargs.get("username", None)
        if other_username == None:
            other_username = 'Alice'

        eventlog('get_object other_username: ' + str(other_username))
        if self.bool_temp_user != True:
            eventlog('self.request.user: ' + str(self.request.user))
            obj, created    = WebharvestThread.objects.get_or_new(self.request.user, other_username)
        else:
            eventlog('self.temp_user: ' + str(self.temp_user))
            obj, created    = WebharvestThread.objects.get_or_new(self.temp_user, other_username)

        if obj == None:
            raise Http404
        return obj
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.bool_temp_user != True:
            context['user_email'] = self.request.user.email
        else:
            context['user_email'] = self.temp_user.email

        context['form'] = self.get_form()
        context['user_ip'] = self.user_ip
        context['the_user'] = self.the_user
        context['ascii_art'] = get_ascii_art()  

        if self.bool_temp_user != True:
            job, new = WebharvestJob.objects.get_or_new(user=self.request.user)
        else:
            eventlog('temp_user: ' + str(self.temp_user))
            job, new = WebharvestJob.objects.get_or_new(user=self.temp_user)

        eventlog('job.somesetting: ' + str(job.somesetting))
        if 'form2' not in context:
            context['form2'] = self.second_form_class()
            context['form2'].initial['somesetting'] = str(job.somesetting)
            context['form2'].initial['search_keywords'] = str(job.search_keywords)

        return context

    def post(self, request, *args, **kwargs):
        # if not request.user.is_authenticated:
        #     return HttpResponseForbidden()
        self.object = self.get_object()

        if 'form' in request.POST:
            form_class = self.get_form_class()
            form_name = 'form'
        else:
            form_class = self.second_form_class
            form_name = 'form2'

        form = self.get_form(form_class)
        eventlog('post -- form: ' + str(form))
        if 'form' in request.POST:
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            if form.is_valid():
                return self.form2_valid(form)
            else:
                return self.form_invalid(form)

    def form_valid(self, form):
        eventlog("form_valid")
        thread = self.get_object()
        if self.bool_temp_user != True:
            user = self.request.user
        else:
            user = self.temp_user
        # user = self.request.user
        eventlog('form_valid user: ' + str(user))
        message = form.cleaned_data.get("message")
        WebharvestChatMessage.objects.create(user=user, thread=thread, message=message)
        return super().form_valid(form)

    def form2_valid(self, form):
        eventlog("form2_valid")
        thread = self.get_object()
        if self.bool_temp_user != True:
            user = self.request.user
        else:
            user = self.temp_user

        eventlog('form_valid user: ' + str(user))

        job, new = WebharvestJob.objects.get_or_new(user=user)
        eventlog('WebharvestJob: ' + str(job))
        job_name = form.cleaned_data.get('job_name')
        job.job_name = job_name
        job.user_email = user.email
        robot = thread.robot
        eventlog('thread robot: ' + str(robot))
        robot_name = robot.robot_name
        eventlog('thread robot_name: ' + str(robot_name))
        job.robot_name = robot_name
        somesetting = form.cleaned_data.get('somesetting')
        job.somesetting = somesetting
        search_keywords = form.cleaned_data.get('search_keywords')
        job.search_keywords = search_keywords
        job.save()

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
        return JsonResponse({'response_message': 'henlo'})
 
    def robot_command_clear(self, human, robot):
        eventlog('delete_extra_messages')
        eventlog('human: ' + str(human) + ' robot: ' + str(robot))
        thread_obj = WebharvestThread.objects.get_or_new(human, robot)[0]
        chat_message_objects = WebharvestChatMessage.objects.filter(thread=thread_obj)
        chat_message_list = []
        for chat_message in chat_message_objects:
            chat_message_list.append(chat_message)

        for i in range(0, len(chat_message_list)):
            WebharvestChatMessage.objects.filter(id=chat_message_list[i].id).delete()

    def post(self, request, *args, **kwargs):
        eventlog('WebHarvestWebhookView POST request: ' + str(request))
        eventlog('WebHarvestWebhookView POST args: ' + str(*args))
        eventlog('WebHarvestWebhookView POST kwargs: ' + str(**kwargs))
        data = request.POST
        eventlog('WebHarvestWebhookView POST data: ' + str(data))
        json.dumps(data)
        eventlog('WebHarvestWebhookView POST json.dumps(data): ' + str(data))
        # return HttpResponse("", status=200)
        if 'human' in data:
            eventlog('user: ' + str(data['human']))
            User = get_user_model()    
            human = str(data['human'])
            eventlog('human: ' + str(human))
            user = User.objects.get(email=human)
            eventlog('post user target: ' + str(user))
            eventlog('post user id: ' + str(user.user_id))

        if 'chat_message' in data:
            eventlog('chat_message: ' + str(data['chat_message']))
            channel_layer = get_channel_layer()
            my_text = {
                    'message': str(data['chat_message']),
                    'username': 'Alice',
                    'From': 'Alice',
                    'command': str(data['command'])
            }
            
            thread_obj = WebharvestThread.objects.get_or_new(human, 'Alice')[0] 
            WebharvestChatMessage.objects.create(thread=thread_obj, user='Alice', message=str(data['chat_message']))

            async_to_sync(channel_layer.group_send, force_new_loop=False)(
                # andre@blackmesanetwork.com user_id
                # 'jj0i1WGGl3S5ZzlQ1qO9',
                #dante
                # "dantegemlc0bw6idqs0edoumad",
                #andre@stringkeeper.com
                str(user.user_id),
                #"xAu8XilVFGYyhnHoh4Sw",
                {
                    'type': 'chat_message',
                    'text': json.dumps(my_text)
                }
            )
        

        if 'command' in data:
            if str(data['command']) == 'clear':
                try:
                    self.robot_command_clear(str(data['human']), str(data['From']))
                except Exception as e:
                    eventlog('EXCEPTION::: ' + str(e))
            


        response = {
            'user': 'Alice',
            'chat': 'the record of chat for user'
        }
        # sleep(0.1)
        return JsonResponse(response)

