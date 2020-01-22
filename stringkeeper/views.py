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
