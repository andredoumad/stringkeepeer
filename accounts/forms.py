from django import forms
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.urls import reverse
from django.utils.safestring import mark_safe

User = get_user_model()

from .models import EmailActivation
from .signals import user_logged_in
from stringkeeper.standalone_tools import *


class ReactivateEmailForm(forms.Form):
    email       = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = EmailActivation.objects.email_exists(email)
        if not qs.exists():
            register_link = reverse("register")
            msg = """This email does not exists, would you like to <a href="{link}">register</a>?
            """.format(link=register_link)
            raise forms.ValidationError(mark_safe(msg))
        return email


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)

    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name',) #'first_name,)   << add required fields here as needed

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False # send confirmation email
        if commit:
            user.save()
        return user


class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    first_name = forms.CharField(
        label= 'First Name',
        widget=forms.TextInput(
           attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control my-2',

            }
        )
    )
    last_name = forms.CharField(
        label= 'Last Name',
        widget=forms.TextInput(
           attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control my-2',

            }
        )
    )
    email = forms.EmailField(
        label= 'Email',
        widget=forms.TextInput(
           attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control my-2',

            }
        )
    )
    # password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password1 = forms.CharField(
        label= 'Password',
        widget=forms.PasswordInput(
           attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control my-2',

            }
        )
    )
    # password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label= 'Password confirmation',
        widget=forms.PasswordInput(
           attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control my-2',

            }
        )
    )

    

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',) #'full_name',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.full_name = str(str(user.first_name) + ' ' + str(user.last_name))
        # obj = EmailActivation.objects.create(user=user) # send confirmation email via signals
        # obj.send_activation_email()
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'is_active', 'admin', )

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class GuestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(
           attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                "placeholder": "email"
            }
        )
    )

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(GuestForm, self).__init__(*args, **kwargs)



class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.TextInput(
            
           attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control my-2',
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
           attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control my-2',

            }
        )
    )

    #allows us to use the request inside of this form !
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is None:
            raise forms.ValidationError("Invalid credentials")
        login(request, user)
        # this is a copy of the actual user object
        self.user = user
        user_logged_in.send(user.__class__, instance=user, request=request)
        try:
            eventlog('try')
            del request.session['guest_email_id']
        except:
            eventlog('except')
            pass
        return data

    # def form_valid(self, form):
    #     print('def form_valid')
    #     request = self.request
    #     next_ = request.GET.get('next')
    #     next_post = request.POST.get('next')
    #     redirect_path = next_ or next_post or None
    #     email = form.cleaned_data.get('email')
    #     password = form.cleaned_data.get('password')
    #     user = authenticate(request, username=email, password=password)

    #     if user is not None:
    #         print('if user is not None')
    #         if not user.is_active:
    #             messages.error(request, str(str(user.email) + " is inactive"))
    #             return super(LoginView, self).form_invalid(form, {'ascii_art': 'ascii_art'})

    #         login(request, user)
    #         user_logged_in.send(user.__class__, instance=user, request=request)
    #         try:
    #             print('try')
    #             del request.session['guest_email_id']
    #         except:
    #             print('except')
    #             pass
    #         if is_safe_url(redirect_path, request.get_host()):
    #             print('is_safe_url')
    #             return redirect(redirect_path)
    #         else:
    #             print('is_safe_url else')
    #             return redirect('/')

    #     return super(LoginView, self).form_invalid(form)