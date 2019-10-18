from django.db import models

# Create your models here.
# allows you to store data

class BlogPost(models.Model):
    # id = models.IntegerField() # pk
    title = models.TextField()
    slug = models.SlugField(unique=True) # url encoded value so hello world -> hello-world
    content = models.TextField(null=True, blank=True)