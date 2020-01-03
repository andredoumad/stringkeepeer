#your going to want this to be in the blog app later
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ContactForm(forms.Form):
    fullname = forms.CharField(
        #docs.djangoproject.com - customizing-widget-instances
        widget=forms.TextInput(
            attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                "class": "form-control", 
            }
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control',
            }
        )
    )
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control',
            }
        )
    )
    

# class LoginForm(forms.Form):
#     username = forms.CharField()
#     password = forms.CharField(
#         widget=forms.PasswordInput()
#     )

# class RegisterForm(forms.Form):
#     username = forms.CharField()
#     email = forms.EmailField()
#     password = forms.CharField(
#         widget=forms.PasswordInput()
#     )
#     password2 = forms.CharField(
#         label='Confirm password',
#         widget=forms.PasswordInput()
#     )

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         qs = User.objects.filter(username=username)
#         if qs.exists():
#             raise forms.ValidationError('Username is taken')
#         return username

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         qs = User.objects.filter(email=email)
#         if qs.exists():
#             raise forms.ValidationError('Email is taken')
#         return email

#     def clean(self):
#         data = self.cleaned_data
#         password = self.cleaned_data.get('password')
#         password2 = self.cleaned_data.get('password2')
#         if password2 != password:
#             raise forms.ValidationError('Passwords must match.')
#         return data

