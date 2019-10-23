from django.db import models
from django.conf import settings
# Create your models here.
# allows you to store data


User = settings.AUTH_USER_MODEL

class BlogPost(models.Model): # blogpost_set -> queryset
    # id = models.IntegerField() # pk
    user = models.ForeignKey(User, default=1, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True) # url encoded value so hello world -> hello-world
    content = models.TextField(null=True, blank=True)