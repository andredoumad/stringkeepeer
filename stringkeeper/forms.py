#your going to want this to be in the blog app later
from django import forms

class ContactForm(forms.Form):
    full_name = forms.CharField()
    email = forms.EmailField()
    content = forms.CharField(widget=forms.Textarea)
    
    #taking args and keyword args 
    def clean_email(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        # u can prevent certain types of emails from here
        # so good place to clean -- data
        #if email.endswith('.edu'):
        #    raise forms.ValidationError("This is not a valid email - don't use .edu")
        print(email)
        return email