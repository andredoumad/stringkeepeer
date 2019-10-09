from django.http import HttpResponse
from django.shortcuts import render

def home_page(request):
    title = 'Hello there...'
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