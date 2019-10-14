import os, time, random
from time import sleep
from random import *
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
import stringkeeper.standalone_tools
import datetime
from django.utils.timezone import utc
from random import randint
tools = stringkeeper.standalone_tools.Tools()

def get_time_string():
    #named_tuple = time.localtime() # get struct_time
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    #time_string = str(time.strftime("%Y-%m-%d-%H:%M:%S", named_tuple))
    #time_string = str(time.strftime("%Y-%m-%d-%H:%M:%S", now))
    return (now)


def get_ascii_art():
    b_dp, b_fp, list_dp, list_fp = tools.get_list_files_folders_in_path('stringkeeper/landing_page_ascii_art')
    list_of_ascii_art_files = list_fp
    shuffled_art_files = tools.shuffle_list(list_of_ascii_art_files)
    chosen_art_file = shuffled_art_files[0]
    list_of_ascii_art_strings = tools.get_list_from_file(chosen_art_file)
    art_string = '\n'
    for line in list_of_ascii_art_strings:
        art_string += str(line)
        art_string += '\n'
    return str(art_string)



def home_page(request):
    title = str('This site is in active development.')
    subtitle = get_time_string()
    ascii_art = get_ascii_art()
    my_title = 'Welcome'
    user_ip = tools.get_client_ip(request)
    if request.user.is_authenticated:
        my_title += str(' ' + str(request.user))
    else:
        my_title += str(' ' + str(' visitor ') + str(user_ip))

    my_list = [1,2,3,4,5]
    context = {'title': my_title}
    template_name   = 'title.txt'
    template_obj    = get_template(template_name)
    rendered_string = template_obj.render(context)
    print(rendered_string)
    #doc = '<h1>{title}</h1>'.format(title=title)
    #django_rendered_doc = '<h1>{{title}}</h1>'.format(title=title)
    #return HttpResponse("<h1>This site is under construction.</h1>")
    return render(request, "home.html", {'home.html': context,
                                         'my_list': my_list,
                                         'title': rendered_string,
                                         'subtitle': subtitle,
                                         'ascii_art': ascii_art})


def about_page(request):
    title = 'About this site...'
    return render(request, "about.html", {'title': title})
    #return HttpResponse("<h1>about.</h1>")


def contact_page(request):
    title = 'Site contact details...'
    return render(request, "base.html", {'title': title})


def example_page(request):
    context         = {'title': 'Example'}
    template_name   = 'hello_world.html'
    template_obj    = get_template(template_name)
    rendered_item   = template_obj.render(context)
    return HttpResponse(template_obj.render(context))