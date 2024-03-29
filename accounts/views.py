from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView
from django.views.generic.edit import FormMixin

from stringkeeper.standalone_tools import *
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe

from .forms import LoginForm, RegisterForm, GuestForm, ReactivateEmailForm, UserDetailChangeForm
from .models import GuestEmail, EmailActivation
from .signals import user_logged_in
from django.urls import reverse
from accounts.mixins import ObjectViewedMixin
from stringkeeper.mixins import NextUrlMixin, RequestFormAttachMixin
from stringkeeper.braintree_tools import get_braintree_customer

# User = get_user_model()

# @login_required
# def account_home_view(request):
#     return render(request, "accounts/home.html", {})

User = get_user_model()

#LoginRequiredMixin,
class AccountHomeView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/home.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AccountHomeView, self).get_context_data(*args, **kwargs)
        context['ascii_art'] = get_ascii_art()
        return context

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
                eventlog('obj: ' + str(obj))
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
                'key': self.key,
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
        eventlog('form_valid')
        msg = """Activation link sent, please check your email."""
        request = self.request
        messages.success(request, msg)
        email = form.cleaned_data.get("email")
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user=user, email=email)
        new_activation.send_activation()
        return super(AccountEmailActivateView, self).form_valid(form)


    def form_invalid(self, form):
    
        context = {
            'form': form, 
            "key": self.key,
            'ascii_art': get_ascii_art()
            }
        return render(self.request, 'registration/activation-error.html', context)



def guest_register_view(NextUrlMixin, request):
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




class LoginView(NextUrlMixin, RequestFormAttachMixin, ObjectViewedMixin, FormView):
    eventlog('LoginView')
    form_class = LoginForm
    success_url = '/'
    template_name = 'accounts/login.html'
    default_next = '/'
    # ascii_art =  get_ascii_art()



    def form_valid(self, form):
        eventlog(str(form.user))
        next_path = self.get_next_url()
        return redirect(next_path)




class RegisterView(ObjectViewedMixin, CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    eventlog('Activated register view')
    success_url = '/login/'



class UserDetailUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserDetailChangeForm
    template_name = 'accounts/detail-update-view.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Change Your Account Details'
        context['ascii_art'] = get_ascii_art()
        return context

    # GOOD EXAMPLE OF HOW TO UPDATE THE USER DATA :) !! ^.^
    def get_success_url(self):
        eventlog('self.request.user: ' + str(self.request.user))
        eventlog('self.request.user.full_name: ' + str(self.request.user.full_name))
        eventlog('self.request.user.first_name: ' + str(self.request.user.first_name))
        eventlog('self.request.user.last_name: ' + str(self.request.user.last_name))
        self.request.user.full_name = str(str(self.request.user.first_name) + ' ' + str(self.request.user.last_name))
        eventlog('self.request.user.full_name: ' + str(self.request.user.full_name))
        User.full_name = self.request.user.full_name
        self.request.user.save()
        customer = get_braintree_customer(self.request)
        return reverse("account:home")
