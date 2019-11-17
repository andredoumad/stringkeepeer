from django.conf import settings
from django.db import models

from subscription.models import Subscription

User = settings.AUTH_USER_MODEL

# Create your models here.
class Cart(models.Model):
    user            = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    subscription    = models.ManyToManyField(Subscription, blank=True)
    total           = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    updated         = models.DateTimeField(auto_now=True)
    timestamp       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)