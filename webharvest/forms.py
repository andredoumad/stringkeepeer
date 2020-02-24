from django import forms
from webharvest.models import WebharvestJob

class ComposeForm(forms.Form):
    message = forms.CharField(
        label = '', required=False,
            widget=forms.TextInput(
                attrs={
                    'style': 'background-color:rgb(35, 39, 43); color: white;',
                    'class': 'form-control my-2',
                    "label": ""
                    }
                )
            )


class WebharvestJobForm(forms.ModelForm):
    job_name = forms.CharField(label='Job Name', required=False, widget=forms.TextInput(attrs={"class": 'form-control'}))
    user_email = forms.CharField(label='User Email', required=False, widget=forms.TextInput(attrs={"class": 'form-control'}))
    robot_name = forms.CharField(label='Robot Name', required=False, widget=forms.TextInput(attrs={"class": 'form-control'}))
    somesetting = forms.CharField(label='Some Setting', required=False, widget=forms.TextInput(attrs={"class": 'form-control'}))

    class Meta:
        model = WebharvestJob
        fields = ['job_name', 'user_email', 'robot_name', 'somesetting']
        # model.full_name = str(str(first_name) + ' ' + str(last_name))