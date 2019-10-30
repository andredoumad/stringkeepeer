import os, time, random
from time import sleep
from random import *
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils import timezone
import stringkeeper.standalone_tools
import datetime
from django.utils.timezone import utc
from random import randint

from stringkeeper.forms import ContactForm
from blog.models import BlogPost

tools = stringkeeper.standalone_tools.Tools()
def get_time_string():
    #named_tuple = time.localtime() # get struct_time
    now = timezone.now()
    #now = datetime.datetime.utcnow().replace(tzinfo=utc)
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
    #title = str('This site is in active development.')
    qs = BlogPost.objects.all()
    print('BlogPost.objects.all()[:5] = ' + str(qs))
    subtitle = get_time_string()
    ascii_art = get_ascii_art()
    my_title = 'Welcome'
    user_ip = tools.get_client_ip(request)
    if request.user.is_authenticated:
        my_title += str(' ' + str(request.user))
    else:
        my_title += str(' ' + str(' visitor ') + str(user_ip))

    #my_list = [1,2,3,4,5]

    #template_name   = 'title.txt'
    #template_obj    = get_template(template_name)
    #rendered_string = template_obj.render(context)
    #print(rendered_string)
    context = {
        'user_ip': user_ip,
        #'my_list': my_list,
        'title': my_title,
        'subtitle': subtitle,
        'ascii_art': ascii_art,
        'blog_list': qs}
    #doc = '<h1>{title}</h1>'.format(title=title)
    #django_rendered_doc = '<h1>{{title}}</h1>'.format(title=title)
    #return HttpResponse("<h1>This site is under construction.</h1>")
    return render(request, "home.html", context)


'''
def about_page(request):
    title = 'About this site...'
    return render(request, "about.html", {'title': title})
    #return HttpResponse("<h1>about.</h1>")

def contact_page(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
        form = ContactForm()
    context = {
        'title': 'Contact us',
        'form': form
    }
    return render(request, "form.html", context)
'''

'''
def example_page(request):
    context         = {'title': 'Example'}
    template_name   = 'base.html'
    template_obj    = get_template(template_name)
    rendered_item   = template_obj.render(context)
    return HttpResponse(template_obj.render(context))
'''