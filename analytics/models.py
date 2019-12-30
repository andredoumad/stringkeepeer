from django.conf import settings
from django.db import models

# Create your models here.
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = settings.AUTH_USER_MODEL

class ObjectViewed(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL) # user instance.id
    # ip_address 
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.SET_NULL) # user, subscription, order, cart, address whatever models are used
    object_id = models.PositiveIntegerField() # user id, product id, order id etc...
    content_object = GenericForeignKey('content_type', 'object_id') # subscription instance etc...
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s viewed %s" %(self.content_object, self.timestamp)

    class Meta:
        ordering = ['-timestamp'] # most recent saved show up first
        verbose_name = 'Object viewed'
        verbose_name_plural = 'Objects viewed'