from django import forms


class ComposeForm(forms.Form):
    message = forms.CharField(
        label = '',
            widget=forms.TextInput(
                attrs={
                    'style': 'background-color:rgb(35, 39, 43); color: white;',
                    'class': 'form-control my-2',
                    "label": ""
                    }
                )
            )