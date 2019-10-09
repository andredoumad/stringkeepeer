from django.http import HttpResponse

def home_page(request):
    return HttpResponse("<h1>This site is under construction.</h1>")