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
from webharvest.models import WebharvestChatMessage, WebharvestThread, WebharvestSpreadSheet, WebharvestSpreadSheetRecord
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
            User = get_user_model()
            def UpdateMessageCounts():
                
                for user in User.objects.all():
                    obj, created    = WebharvestThread.objects.get_or_new(user, 'Alice')

                    # thread_obj = WebharvestThread.objects.get_or_new(human, robot)[0]
                    eventlog('WebharvestThread obj: ' + str(obj))


                    chat_message_objects = WebharvestChatMessage.objects.filter(thread=obj)
                    
                    for chat_message in chat_message_objects:
                        # chat_message_list.append(chat_message)
                        eventlog('WebharvestThread chat_message: ' + str(chat_message))

                    # for i in range(0, len(chat_message_list)):
                    #     WebharvestChatMessage.objects.filter(id=chat_message_list[i].id).delete()

                    obj.message_count = len(chat_message_objects)
                    obj.save()
                    
                    sleep(0.1)

            # UpdatedMessageCounts()

            def CreateWebharvestSpreadsheet():
                eventlog('CreateWebharvestSpreadsheet')
                thread_obj = WebharvestThread.objects.get_or_new(request.user.email, 'Alice')[0] 
                if thread_obj.spreadsheet == None:
                    eventlog('CreateWebharvestSpreadsheet SPREADSHEET IS NONE! creating spreadsheet!')
                    WebharvestSpreadSheet.objects.create(thread=thread_obj)
                
                eventlog('finding spreadsheet and setting it to the webharvest thread spreadsheet variable') 

                spreadsheet_objects = WebharvestSpreadSheet.objects.filter(thread=thread_obj)
                
                for spreadsheet in spreadsheet_objects:
                    # chat_message_list.append(chat_message)
                    eventlog('spreadsheet: ' + str(spreadsheet))
                    thread_obj.spreadsheet = spreadsheet
                
                thread_obj.save()
            
            # CreateWebharvestSpreadsheet()




            #how can i consolidate the async version of this method from consumers.py into one method?
            def robot_command_clear():
                for user in User.objects.all():
                    human = user
                    robot = 'Alice'
                    try:
                        eventlog('robot_command_clear')
                        eventlog('human: ' + str(human) + ' robot: ' + str(robot))
                        thread_obj = WebharvestThread.objects.get_or_new(human, robot)[0]

                        eventlog('self.thread_obj: ' + str(thread_obj))
                        chat_message_objects = WebharvestChatMessage.objects.filter(thread=thread_obj)
                        eventlog('chat_message_objects: ' + str(chat_message_objects))

                        chat_message_list = []

                        for chat_message in chat_message_objects:
                            chat_message_list.append(chat_message)


                        eventlog('length of chat_message_list: ' + str(len(chat_message_list)))

                        for chat_message in chat_message_list:
                            eventlog('message: ' + str(chat_message))

                        for i in range(0, len(chat_message_list)):
                            eventlog('deleting ' + str(i) + ' of ' + str(len(chat_message_list)))
                            eventlog('chat_message_id: ' + str(chat_message_list[i].id))
                            WebharvestChatMessage.objects.filter(id=chat_message_list[i].id).delete()


                        records = WebharvestSpreadSheetRecord.objects.filter(spreadsheet=thread_obj.spreadsheet)
                        records_list = []
                        eventlog('about to cycle through SPREADSHEET records: ')
                        eventlog('records: ' + str(records))
                        
                        for record in records:
                            eventlog('appending record: ' + str(record))
                            records_list.append(record)
                        
                        for i in range(0, len(records_list)):
                            # eventlog('record: ' + str(WebharvestSpreadSheetRecord.objects.filter(id=records_list[i].id)))
                            WebharvestSpreadSheetRecord.objects.filter(id=records_list[i].id).delete()


                        thread_obj.spreadsheet.record_count = 0
                        thread_obj.spreadsheet.save()
                    except Exception as e:
                        eventlog('EXCEPTION: ' + str(e))

            robot_command_clear()


            context         = {'title': 'maintenance_page'}
            template_name   = 'maintenance_page.html'
            template_obj    = get_template(template_name)
            rendered_item   = template_obj.render(context)
            return HttpResponse(template_obj.render(context))
        else:
            eventlog('maintenance_page andre is not logged in! ')
            return redirect('webharvest')
