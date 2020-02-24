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

from .forms import ComposeForm, WebharvestJobForm
from django.views.generic.edit import FormMixin
from .models import WebharvestThread, WebharvestChatMessage, WebharvestJob
from webharvest.consumers import WebharvestConsumer

from .multiform import *

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from django.contrib.auth import get_user_model

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


# # class ThreadView(LoginRequiredMixin, FormMixin, DetailView):
# class ThreadView(LoginRequiredMixin, MultiFormMixin, DetailView):
#     template_name = 'webharvest/thread.html'
#     form_classes = {
#         'form': ComposeForm,
#         'form2': WebharvestJob
#     }
#     success_url = './'

#     # def get_form_initial(self):
#     #     return {'message':'testing'}

#     # def get_form2_initial(self):
#     #     return {'user_email':'dave@dave.com'}


#     def get_queryset(self):
#         return WebharvestThread.objects.by_user(self.request.user)

#     def get_object(self):
#         other_username  = self.kwargs.get("username", None)
#         if other_username == None:
#             other_username = 'Alice'

#         eventlog('get_object other_username: ' + str(other_username))

#         eventlog('self.request.user: ' + str(self.request.user))
#         obj, created    = WebharvestThread.objects.get_or_new(self.request.user, other_username)
#         if obj == None:
#             raise Http404
#         return obj
        

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         forms = self.get_form_classes()
#         context['form'] = self.get_forms(forms, 'form')

#         context['form2'] = self.get_forms(forms, 'form2')
#         for item in context:
#             eventlog('context item: ' + str(item))
#             if item == 'form2':
#                 eventlog('context item' + str(item.user_email))
#         return context

#     def post(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return HttpResponseForbidden()
#         self.object = self.get_object()
#         forms = self.get_form_classes()
#         form = None
#         for a_form in forms:
#             if 'form' in request.POST:
#                 if str(a_form) == 'form':
#                     eventlog('form: ' + str(a_form))
#                     form = a_form
        
#         self.forms_valid(forms, 'form')
        
#         return self.forms_valid(forms, 'form')
#         # if forms[0].is_valid():
#         #     return self.form_valid(form)
#         # else:
#         #     return self.form_invalid(form)

#     def form_valid(self, form):
#         thread = self.get_object()
#         user = self.request.user
#         eventlog('form_valid user: ' + str(user))
#         message = form.cleaned_data.get("message")
#         WebharvestChatMessage.objects.create(user=user, thread=thread, message=message)
#         return super().form_valid(form)







class ThreadView(LoginRequiredMixin, FormMixin, DetailView):

    template_name = 'webharvest/thread.html'
    form_class = ComposeForm
    second_form_class = WebharvestJobForm
    success_url = './'

    def get_queryset(self):
        return WebharvestThread.objects.by_user(self.request.user)

    def get_object(self):
        other_username  = self.kwargs.get("username", None)
        if other_username == None:
            other_username = 'Alice'

        eventlog('get_object other_username: ' + str(other_username))

        eventlog('self.request.user: ' + str(self.request.user))
        obj, created    = WebharvestThread.objects.get_or_new(self.request.user, other_username)
        if obj == None:
            raise Http404
        return obj
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        job, new = WebharvestJob.objects.get_or_new(user=self.request.user)
        eventlog('job.somesetting: ' + str(job.somesetting))
        if 'form2' not in context:
            context['form2'] = self.second_form_class()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
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
        user = self.request.user
        eventlog('form_valid user: ' + str(user))
        message = form.cleaned_data.get("message")
        WebharvestChatMessage.objects.create(user=user, thread=thread, message=message)
        return super().form_valid(form)

    def form2_valid(self, form):
        eventlog("form2_valid")
        thread = self.get_object()
        user = self.request.user
        eventlog('form_valid user: ' + str(user))
        # user_email = form.cleaned_data.get("user_email")
        job_name = form.cleaned_data.get('job_name')
        somesetting = form.cleaned_data.get('somesetting')
        # thread = WebharvestThread.objects.by_user(self.request.user)
        
        robot = thread.robot
        eventlog('thread robot: ' + str(robot))
        robot_name = robot.robot_name
        eventlog('thread robot_name: ' + str(robot_name))

        job, new = WebharvestJob.objects.get_or_new(user=self.request.user)
        eventlog('WebharvestJob: ' + str(job))
        job.job_name = job_name
        job.user_email = self.request.user.email
        job.robot_name = robot_name
        job.somesetting = somesetting
        job.save()

        # WebharvestJob.objects.create(user_email=self.request.user.email)
        return super().form_valid(form)








# class ThreadView(LoginRequiredMixin, FormMixin, DetailView):

#     template_name = 'webharvest/thread.html'
#     form_class = ComposeForm
#     success_url = './'

#     def get_queryset(self):
#         return WebharvestThread.objects.by_user(self.request.user)

#     def get_object(self):
#         other_username  = self.kwargs.get("username", None)
#         if other_username == None:
#             other_username = 'Alice'

#         eventlog('get_object other_username: ' + str(other_username))

#         eventlog('self.request.user: ' + str(self.request.user))
#         obj, created    = WebharvestThread.objects.get_or_new(self.request.user, other_username)
#         if obj == None:
#             raise Http404
#         return obj
        

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = self.get_form()
#         return context

#     def post(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return HttpResponseForbidden()
#         self.object = self.get_object()
#         form = self.get_form()
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)

#     def form_valid(self, form):
#         thread = self.get_object()
#         user = self.request.user
#         eventlog('form_valid user: ' + str(user))
#         message = form.cleaned_data.get("message")
#         WebharvestChatMessage.objects.create(user=user, thread=thread, message=message)
#         return super().form_valid(form)



class WebHarvestWebhookView(CsrfExemptMixin, View): # HTTP GET -- def get() CSRF?????
    def get(self, request, *args, **kwargs):
        eventlog('WebHarvestWebhookView GET request: ' + str(request))
        eventlog('WebHarvestWebhookView GET args: ' + str(*args))
        eventlog('WebHarvestWebhookView GET kwargs: ' + str(**kwargs))
        data = request.GET
        eventlog('WebHarvestWebhookView GET data: ' + str(data))
        json.dumps(data)
        eventlog('WebHarvestWebhookView GET json.dumps(data): ' + str(data))
        # return HttpResponse("hello", status=200)

        # if 'getter' in data:
        #     eventlog('getter is in data....')
        #     if str(data['getter']) == 'webharvest_robot_router':
        #         eventlog('getter is webharvest_robot_router....')
        #         eventlog('generating list of active webharvest chatroom users')

        #         active_users = {}
        #         inactive_users = {}
        #         User = get_user_model()
        #         for item in User.objects.all():
        #             eventlog('User: ' + str(item))
        #             if item.bool_webharvest_chat_active == True:
        #                 active_users[item.email] = item.webharvest_robot_name
        #             else:
        #                 inactive_users[item.email] = item.webharvest_robot_name
        #         return JsonResponse({
        #             'active_users': json.dumps(active_users),
        #             'inactive_users': json.dumps(inactive_users)
        #             })
        return JsonResponse({'response_message': 'henlo'})
 

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
            channel_layer = get_channel_layer()
            # async_to_sync(channel_layer.group_send)(
            #     'thread_1',
            #     {
            #         'type': 'send_message_to_frontend',
            #         'text': str(data['chat_message'])
            #     }
            # )
            my_text = {
                    'message': str(data['chat_message']),
                    'username': 'Alice'
            }
            thread_obj = WebharvestThread.objects.get_or_new('dante@stringkeeper.com', 'Alice')[0]
            WebharvestChatMessage.objects.create(thread=thread_obj, user='Alice', message=str(data['chat_message']))
            # asyncio.get_event_loop().run_until_complete(command_receiver())

            async_to_sync(channel_layer.group_send, force_new_loop=False)(
                # andre@blackmesanetwork.com user_id
                # 'jj0i1WGGl3S5ZzlQ1qO9',
                #dante
                "dantegemlc0bw6idqs0edoumad",
                #andre@stringkeeper.com
                #"xAu8XilVFGYyhnHoh4Sw",
                {
                    'type': 'chat_message',
                    'text': json.dumps(my_text)
                }
            )



            # async_to_sync(channel_layer.group_send, force_new_loop=True)(
            #     # andre@blackmesanetwork.com user_id
            #     # 'jj0i1WGGl3S5ZzlQ1qO9',
            #     #dante
            #     "dantegemlc0bw6idqs0edoumad",
            #     #andre@stringkeeper.com
            #     #"xAu8XilVFGYyhnHoh4Sw",
            #     {
            #         'type': 'chat_message_from_robot',
            #         'text': json.dumps(my_text)
            #     }
            # )



        response = {
            'user': 'Alice',
            'chat': 'the record of chat for user'
        }
        # sleep(0.1)
        return JsonResponse(response)

