from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField

User = get_user_model()

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
        if commit:
            user.save()
        return user


class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    # password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password1 = forms.CharField(
        widget=forms.PasswordInput(
           attrs={
                'label': 'Password',
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control',

            }
        )
    )
    # password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    password2 = forms.CharField(
        widget=forms.PasswordInput(
           attrs={
                'label': 'Password confirmation',
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control',

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
        # user.is_active = False # send confirmation email via signals
        # obj = EmailActivation.objects.create(user=user)
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
                'class': 'form-control',
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
           attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control',

            }
        )
    )

    # def __init__(self, request, *args, **kwargs):
    #     self.request = request
    #     super(LoginForm, self).__init__(*args, **kwargs)
