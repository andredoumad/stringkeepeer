from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect

from stringkeeper.forms import LoginForm, RegisterForm
# Create your views here.
from stringkeeper.standalone_tools import *
from django.utils.http import is_safe_url

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
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        eventlog(form.cleaned_data)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        eventlog(str(user))
        #print(str(request.user.is_authenticated))
        if user is not None:
            #redirect to success page
            #print(str(request.user.is_authenticated))
            login(request, user)
            #context['form'] = LoginForm()
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:

                return redirect('/')
        else:
            #return an invalid login message
            eventlog('Error')

    return render(request, "accounts/login.html", context)

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
        eventlog(form.cleaned_data)
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        new_user = User.objects.create_user(username, email, password)
        eventlog(new_user)
    return render(request, "accounts/register.html", context)
