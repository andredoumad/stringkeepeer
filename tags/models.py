import os
from django.db import models
from stringkeeper.utils import unique_slug_generator
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
# Create your models here.

from subscription.models import Subscription


class Tag(models.Model):
    title           = models.CharField(max_length=120)
    slug            = models.SlugField()
    timestamp       = models.DateTimeField(auto_now_add=True)
    active          = models.BooleanField(default=True)
    subscriptions   = models.ManyToManyField (Subscription, blank=True)

    def __str__(self):
        return self.title

def tag_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(tag_pre_save_receiver, sender=Tag)