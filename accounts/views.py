from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse
from django.views.generic import CreateView, FormView
from django.shortcuts import render, redirect

from .forms import LoginForm, RegisterForm, GuestForm
from .models import GuestEmail
# Create your views here.
from stringkeeper.standalone_tools import *
from django.utils.http import is_safe_url


def guest_register_view(request):
    eventlog('LOGIN_PAGE -- ACCOUNTS')
    ascii_art = get_ascii_art()
    form = GuestForm(request.POST or None)
    context = {
        'form': form,
        'ascii_art': ascii_art
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        email = form.cleaned_data.get('email')
        new_guest_email = GuestEmail.objects.create(email=email)
        request.session['guest_email_id'] = new_guest_email.id
        if is_safe_url(redirect_path, request.get_host()):
            eventlog('safe url')
            return redirect(redirect_path)
        else:
            eventlog('not safe url')
            return redirect('/register/')

    return redirect('/register/')

class LoginView(FormView):
    form_class = LoginForm
    success_url = '/'
    template_name = 'accounts/login.html'


    def form_valid(self, form):
        request = self.request
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            try:
                del request.session['guest_email_id']
            except:
                pass
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect('/')
        return super(LoginView, self).form_invalid(form)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    eventlog('Activated register view')
    success_url = '/login/'




# def login_page(request):
#     eventlog('LOGIN_PAGE -- ACCOUNTS')
#     ascii_art = get_ascii_art()
#     #djangoproject.com - how-to-log-a-user-in
#     form = LoginForm(request.POST or None)
#     context = {
#         'form': form,
#         'ascii_art': ascii_art
#     }
#     #print('request.user.is_authenticated: ' + 
#     #str(request.user.is_authenticated))
#     next_ = request.GET.get('next')
#     next_post = request.POST.get('next')
#     redirect_path = next_ or next_post or None
#     eventlog(str(redirect_path))
#     if form.is_valid():
#         eventlog(form.cleaned_data)
#         username = form.cleaned_data.get('username')
#         password = form.cleaned_data.get('password')
#         user = authenticate(request, username=username, password=password)
#         eventlog(str(user))
#         #print(str(request.user.is_authenticated))
#         if user is not None:
#             eventlog('user is none')
#             #redirect to success page
#             #print(str(request.user.is_authenticated))
#             login(request, user)
#             try:
#                 del request.session['guest_email_id']
#             except:
#                 pass
#             #context['form'] = LoginForm()
#             if is_safe_url(redirect_path, request.get_host()):
#                 eventlog('safe url')
#                 return redirect(redirect_path)
#             else:
#                 eventlog('not safe url')
#                 return redirect('/')
#         else:
#             #return an invalid login message
#             eventlog('Error')

#     return render(request, "accounts/login.html", context)



# User = get_user_model()

# def register_page(request):
#     ascii_art = get_ascii_art()
#     form = RegisterForm(request.POST or None)

#     context = {
#         'form': form,
#         'activated': True,
#         'ascii_art': ascii_art,
#     }

#     if form.is_valid():
#         form.save()

#     return render(request, "accounts/register.html", context)
