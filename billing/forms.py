from django import forms

from .models import BillingProfile

from django.db.models import Q

class PaymentMethodForm(forms.ModelForm):


    class Meta:
        model = BillingProfile
        fields = ('first_name', 'last_name', 'street', 'postal_code',)

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
    street = forms.CharField(
        label= 'street',
        widget=forms.TextInput(
           attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control my-2',

            }
        )
    )
    postal_code = forms.CharField(
        label= 'postal code',
        widget=forms.TextInput(
           attrs={
                'style': 'background-color:rgb(35, 39, 43); color: white;',
                'class': 'form-control my-2',

            }
        )
    )