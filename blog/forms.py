
from django import forms
from blog.models import BlogPost
from stringkeeper.standalone_tools import *

class BlogPostForm(forms.Form):
    title = forms.CharField()
    slug = forms.SlugField()
    content = forms.CharField(widget=forms.Textarea)

class BlogPostModelForm(forms.ModelForm):
    #could overide datatype like this.
    #title = forms.CharField()
    class Meta:
        model = BlogPost
        fields = ['title', 'image', 'slug', 'content', 'publish_date']


    #taking args and keyword args 
    def clean_title(self, *args, **kwargs):
        #how to show all of the components of this object - for listing things like instance
        eventlog(str(str('eventlog(dir(self)): ') + str(dir(self))))
        instance = self.instance
        eventlog(str('instance: ') + str(instance)) # if instance is none - that means its a new blog post
        title = self.cleaned_data.get('title')
        #here's a way we can check for duplicate titles
        #iexact means it doesnt matter if it's using upper or lowercase
        # see https://docs.djangoproject.com/en/2.2/ref/models/querysets/
        qs = BlogPost.objects.filter(title__iexact=title)
        if instance is not None:
            # so if we are updating a blog and not creating one...
            # so take a query set that matches this title, or whatever
            # then we don't want the validation error on the instance we are changing
            qs = qs.exclude(pk=instance.pk) # id = instance.id
        if qs.exists():
            raise forms.ValidationError("This title has already been used.")
        eventlog(title)
        return title