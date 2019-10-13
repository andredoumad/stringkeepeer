import os, time, random
from time import sleep
from random import *
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
import stringkeeper.standalone_tools
import datetime
from django.utils.timezone import utc
tools = stringkeeper.standalone_tools.Tools()

def get_time_string():
    #named_tuple = time.localtime() # get struct_time
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    #time_string = str(time.strftime("%Y-%m-%d-%H:%M:%S", named_tuple))
    #time_string = str(time.strftime("%Y-%m-%d-%H:%M:%S", now))
    return (now)


def get_content():
    b_dp, b_fp, list_dp, list_fp = tools.get_list_files_folders_in_path('stringkeeper/landing_page_ascii_art')
    list_of_ascii_art_files = list_fp
    shuffled_art_files = tools.shuffle_list(list_of_ascii_art_files)
    chosen_art_file = shuffled_art_files[0]
    list_of_ascii_art_strings = tools.get_list_from_file(chosen_art_file)
    art_string = ''
    for line in list_of_ascii_art_strings:
        art_string += str(line)
        art_string += '\n'
    return str(art_string)


def home_page(request):
    title = str('You found the stringkeeper.')
    subtitle = get_time_string()
    content = get_content()
    #doc = '<h1>{title}</h1>'.format(title=title)
    #django_rendered_doc = '<h1>{{title}}</h1>'.format(title=title)
    #return HttpResponse("<h1>This site is under construction.</h1>")
    return render(request, "base.html", {'title': title,
                                         'subtitle': subtitle,
                                         'content': content})


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