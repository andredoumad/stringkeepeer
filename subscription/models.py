import random, os
from django.db import models

# Create your models here.

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    print(instance)
    print(filename)
    new_filename = random.randint(1,9999999999)
    name, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'.format(
        new_filename=new_filename, 
        ext=ext
        )
    return 'subscription/{new_filename}/{final_filename}'.format(
        new_filename=new_filename,
        final_filename=final_filename
        )

class Subscription(models.Model): 
    title           = models.CharField(max_length=120)
    description     = models.TextField()
    price           = models.DecimalField(max_digits=20,  decimal_places=2)
    image           = models.ImageField(upload_to=upload_image_path, null=True, blank=True)

    #this will show the overriding the 'class name' by the title string
    def __str__(self):
        return self.title