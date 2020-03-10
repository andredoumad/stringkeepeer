import os, time, random, socket
from time import sleep
from random import *
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template

from stringkeeper.standalone_tools import *

from django.utils.timezone import utc
from random import randint
from django.contrib.auth import authenticate, login, get_user_model
from .forms import ContactForm
from blog.models import BlogPost
from webharvest.models import WebharvestChatMessage
import requests

#definition for wsgi 
#Web Server Gateway Interface wsgi 


def home_page(request):
    #eventlog('firstname: ' + request.session.get('first_name', 'Unknown'))
    #title = str('This site is in active development.')
    qs = BlogPost.objects.all()
    eventlog('BlogPost.objects.all()[:5] = ' + str(qs))
    subtitle = get_time_string()
    ascii_art = get_ascii_art()
    my_title = 'Welcome'
    user_ip = get_client_ip(request)
    if request.user.is_authenticated:
        my_title += str(' ' + str(request.user) + '.')
    else:
        my_title += str(' ' + str(' visitor ') + str(user_ip))

    context = {
        'user_ip': user_ip,
        'title': my_title,
        'subtitle': subtitle,
        'ascii_art': ascii_art,
        'blog_list': qs
        }
    return render(request, "home.html", context)

def about_page(request):
    context = {
        'title': 'About this site...',
        'ascii_art': get_ascii_art()  

    }
    return render(request, "about.html", context)
    #return HttpResponse("<h1>about.</h1>")


def preview_page(request):
    context = {
        'title': 'preview',
        'ascii_art': get_ascii_art()  

    }
    return render(request, "preview.html", context)
    #return HttpResponse("<h1>about.</h1>")

def contact_page(request):
    ascii_art = get_ascii_art()
    contact_form = ContactForm(request.POST or None)
    
    if contact_form.is_valid():
        eventlog(contact_form.cleaned_data)
        if request.is_ajax():
            return JsonResponse({"message": "Thank you"})
        # contact_form = ContactForm()

    if contact_form.errors:
        eventlog(contact_form.cleaned_data)
        errors = contact_form.errors.as_json()
        if request.is_ajax():
            return HttpResponse(errors, status=400, content_type='application/json')

        # contact_form = ContactForm()    
    context = {
        'title': 'Contact',
        'content': 'Send us an inquiry',
        'form': contact_form,
        'ascii_art': ascii_art
    }
    return render(request, "contact/view.html", context)

def example_page(request):
    ascii_art = get_ascii_art()
    context         = {'title': 'Example'}
    template_name   = 'base.html'
    template_obj    = get_template(template_name)
    rendered_item   = template_obj.render(context)
    return HttpResponse(template_obj.render(context))


def maintenance_page(request):
    eventlog('str(request.user): ' + str(request.user))
    if str(request.user) != 'AnonymousUser':

        if request.user.email == 'andre@stringkeeper.com':

            # cycle through all the messages pertaining to a specific user
            # chat_message_objects = WebharvestChatMessage.objects.filter(user='andre@stringkeeper.com')
            # for chat_message in chat_message_objects:
            #     eventlog('chat_message: ' + str(chat_message))

            User = get_user_model()
            for user in User.objects.all():
                if user.last_name.find('temporary') != -1:
                    geo_request_url = 'https://get.geojs.io/v1/ip/geo/' + str(user.temporary_user_ip) + '.json'
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
                    user.save()
                sleep(1)

            # geo_request_url = 'https://get.geojs.io/v1/ip/geo/' + str('68.231.221.181') + '.json'
            # geo_request = requests.get(geo_request_url)
            # geo_data = geo_request.json()
            # eventlog(geo_data)
            # for key, value in geo_data.items():
            #     eventlog('item: ' + str(key) + ' : ' + str(value))

            # |==| 00114 |==| per/stringkeeper/views.py | maintenance_page | {'organization_name': 'ASN-CXA-ALL-CCI-22773-RDC', 'region': 'California', 'accuracy': 5, 'asn': 22773, 'organization': 'AS22773 ASN-CXA-ALL-CCI-22773-RDC', 'timezone': 'America/Los_Angeles', 'longitude': '-117.7109', 'country_code3': 'USA', 'area_code': '0', 'ip': '68.231.221.181', 'city': 'Laguna Niguel', 'country': 'United States', 'continent_code': 'NA', 'country_code': 'US', 'latitude': '33.5157'} |==|
            
            # User = get_user_model()
            # for user in User.objects.all():
            #     if user.last_name.find('temporary') != -1:
            #         user.bool_temporary_user = True
            #         user.save()

            context         = {'title': 'maintenance_page'}
            template_name   = 'maintenance_page.html'
            template_obj    = get_template(template_name)
            rendered_item   = template_obj.render(context)
            return HttpResponse(template_obj.render(context))
        else:
            eventlog('maintenance_page andre is not logged in! ')
            return redirect('webharvest')
