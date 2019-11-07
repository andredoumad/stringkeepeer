import random, os
from django.db import models
from stringkeeper.standalone_logging import *
from .utils import unique_slug_generator
from django.db.models.signals import pre_save, post_save
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


class SubscriptionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)

class SubscriptionManager(models.Manager):
    def get_queryset(self):
        return SubscriptionQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self): #Subscription.objects.featured()
        return self.get_queryset().featured()
        
    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id) #Subscription.objects self.get_que
        if qs.count() == 1:
            return qs.first() 
        return None

class Subscription(models.Model): 
    title           = models.CharField(max_length=120)
    slug            = models.SlugField(blank=True, unique=True)
    description     = models.TextField()
    price           = models.DecimalField(max_digits=20,  decimal_places=2)
    image           = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    featured        = models.BooleanField(default=False)
    active          = models.BooleanField(default=True)

    objects = SubscriptionManager()
    
    def get_absolute_url(self):
        return "/subscriptions/{slug}/".format(slug=self.slug)

    #this will show the overriding the 'class name' by the title string
    def __str__(self):
        return self.title


def subscription_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(subscription_pre_save_receiver, sender=Subscription)