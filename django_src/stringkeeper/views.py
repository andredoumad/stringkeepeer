import os, time, random
from time import sleep
from random import *
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template


def get_time_string():
    named_tuple = time.localtime() # get struct_time
    time_string = time.strftime("%Y-%m-%d-%H:%M:%S", named_tuple)
    return (time_string)

def home_page(request):
    title = str('You found the stringkeeper. The timestamp is: ' + get_time_string())
    #doc = '<h1>{title}</h1>'.format(title=title)
    #django_rendered_doc = '<h1>{{title}}</h1>'.format(title=title)
    #return HttpResponse("<h1>This site is under construction.</h1>")
    return render(request, "base.html", {'title': title})


def about_page(request):
    title = 'About this site...'
    return render(request, "about.html", {'title': title})
    #return HttpResponse("<h1>about.</h1>")


def contact_page(request):
    title = 'Site contact details...'
    return render(request, "base.html", {'title': title})


def example_page(request):
    context = {'title': 'example'}
    template_name = 'base.html'
    template_obj = get_template(template_name)
    rendered_item = template_obj.render(context)
    return HttpResponse(template_obj.render(context))