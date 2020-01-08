from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse
from django.views.generic import CreateView, FormView, DetailView
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView
from django.views.generic.edit import FormMixin

from stringkeeper.standalone_tools import *
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe

from .forms import LoginForm, RegisterForm, GuestForm, ReactivateEmailForm
from .models import GuestEmail, EmailActivation
from .signals import user_logged_in

from accounts.mixins import ObjectViewedMixin

# User = get_user_model()

# @login_required
# def account_home_view(request):
#     return render(request, "accounts/home.html", {})


#LoginRequiredMixin,
class AccountHomeView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/home.html'
    def get_object(self):
        return self.request.user



class AccountEmailActivateView(FormMixin, View):
    eventlog('AccountEmailActivateView')
    success_url = '/login/'
    form_class = ReactivateEmailForm
    key = None
    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            confirm_qs = qs.confirmable()
            if confirm_qs.count() == 1:
                obj = confirm_qs.first()
                obj.activate()
                messages.success(request, "Your email has been confirmed. Please login.")
                eventlog('confirm_qs.count() == 1')
                return redirect("auth_login")
            else:
                activated_qs = qs.filter(activated=True)
                if activated_qs.exists():
                    reset_link = reverse("password_reset")
                    msg = """Your email has already been confirmed
                    Do you need to <a href="{link}">reset your password</a>?
                    """.format(link=reset_link)
                    messages.success(request, mark_safe(msg))
                    eventlog('activated_qs.exists()')
                    return redirect("auth_login") 
        context = {
                'form': self.get_form(),
                'key': key,
                'ascii_art': get_ascii_art()
            }
        return render(request, 'registration/activation-error.html', context)

    def post(self, request, *args, **kwargs):
        # create form to receive an email
        form = self.get_form()
        if form.is_valid():
            eventlog('post form_valid')
            return self.form_valid(form)
        else:
            eventlog('post form_invalid')
            return self.form_invalid(form)

    def form_valid(self, form):
        msg = """Activation link sent, please check your email."""
        request = self.request
        messages.success(request, msg)
        email = form.cleaned_data.get("email")
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user 
        new_activation = EmailActivation.objects.create(user=user, email=email)
        new_activation.send_activation()
        eventlog('form_valid')
        return super(AccountEmailActivateView, self).form_valid(form)

    def form_invalid(self, form):
    
        context = {
            'form': form, 
            "key": self.key,
            'ascii_art': get_ascii_art()
            }
        return render(self.request, 'registration/activation-error.html', context)



def guest_register_view(request):
    eventlog('LOGIN_PAGE -- ACCOUNTS')
    form = GuestForm(request.POST or None)
    context = {
        'form': form,
        'ascii_art': get_ascii_art()
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

class LoginView(ObjectViewedMixin, FormView):
    eventlog('LoginView')
    form_class = LoginForm
    success_url = '/'
    template_name = 'accounts/login.html'
    ascii_art =  get_ascii_art()


    def form_valid(self, form):
        eventlog('def form_valid')
        request = self.request
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            eventlog('if user is not None')
            if not user.is_active:
                messages.error(request, str(str(user.email) + " is inactive"))
                return super(LoginView, self).form_invalid(form, {'ascii_art': 'ascii_art'})

            login(request, user)
            user_logged_in.send(user.__class__, instance=user, request=request)
            try:
                eventlog('try')
                del request.session['guest_email_id']
            except:
                eventlog('except')
                pass
            if is_safe_url(redirect_path, request.get_host()):
                eventlog('is_safe_url')
                return redirect(redirect_path)
            else:
                eventlog('is_safe_url else')
                return redirect('/')

        return super(LoginView, self).form_invalid(form)



class RegisterView(ObjectViewedMixin, CreateView):
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
