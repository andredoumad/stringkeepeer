
from django import forms
from blog.models import BlogPost

class BlogPostForm(forms.Form):
    title = forms.CharField()
    slug = forms.SlugField()
    content = forms.CharField(widget=forms.Textarea)

class BlogPostModelForm(forms.ModelForm):
    #could overide datatype like this.
    #title = forms.CharField()
    class Meta:
        model = BlogPost
        fields = ['title', 'slug', 'content']


    #taking args and keyword args 
    def clean_title(self, *args, **kwargs):
        title = self.cleaned_data.get('title')
        #here's a way we can check for duplicate titles
        #iexact means it doesnt matter if it's using upper or lowercase
        # see https://docs.djangoproject.com/en/2.2/ref/models/querysets/
        qs = BlogPost.objects.filter(title__iexact=title)
        if qs.exists():
            raise forms.ValidationError("This title has already been used.")
        print(title)
        return title