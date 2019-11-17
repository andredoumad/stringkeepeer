import os, time, random, socket
from time import sleep
from random import *
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.utils import timezone
import stringkeeper.standalone_tools
import datetime
from django.utils.timezone import utc
from random import randint
from django.contrib.auth import authenticate, login, get_user_model
from .forms import ContactForm, LoginForm, RegisterForm
from blog.models import BlogPost

#definition for wsgi 
#Web Server Gateway Interface wsgi 

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

    context = {
        'user_ip': user_ip,
        'title': my_title,
        'subtitle': subtitle,
        'ascii_art': ascii_art,
        'blog_list': qs
        }
    return render(request, "home.html", context)

def about_page(request):
    title = 'About this site...'
    return render(request, "about.html", {'title': title})
    #return HttpResponse("<h1>about.</h1>")

def contact_page(request):
    ascii_art = get_ascii_art()
    contact_form = ContactForm(request.POST or None)
    
    if contact_form.is_valid():
        print(contact_form.cleaned_data)
        form = ContactForm()
    
    context = {
        'title': 'Contact',
        'content': 'Send us an inquiry: ',
        'form': contact_form,
        'ascii_art': ascii_art
    }
    return render(request, "contact/view.html", context)

def login_page(request):
    ascii_art = get_ascii_art()
    #djangoproject.com - how-to-log-a-user-in
    form = LoginForm(request.POST or None)
    context = {
        'form': form,
        'ascii_art': ascii_art
    }
    #print('request.user.is_authenticated: ' + 
    #str(request.user.is_authenticated))
    if form.is_valid():
        print(form.cleaned_data)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        print(str(user))
        #print(str(request.user.is_authenticated))
        if user is not None:
            #redirect to success page
            #print(str(request.user.is_authenticated))
            login(request, user)
            context['form'] = LoginForm()
            return redirect('/')
        else:
            #return an invalid login message
            print('Error')

    return render(request, "auth/login.html", context)

User = get_user_model()
def register_page(request):
    ascii_art = get_ascii_art()
    form = RegisterForm(request.POST or None)
    if socket.gethostname() == 'www.stringkeeper.com':
        
        context = {
            'content': 'Registration is not available on the production server during construction.',
            'activated': False,
            'ascii_art': ascii_art,
        }
    else:
        context = {
            'form': form,
            'activated': True,
            'ascii_art': ascii_art,
        }
    if form.is_valid():
        print(form.cleaned_data)
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        new_user = User.objects.create_user(username, email, password)
        print(new_user)
    return render(request, "auth/register.html", context)

def example_page(request):
    ascii_art = get_ascii_art()
    context         = {'title': 'Example'}
    template_name   = 'base.html'
    template_obj    = get_template(template_name)
    rendered_item   = template_obj.render(context)
    return HttpResponse(template_obj.render(context))
