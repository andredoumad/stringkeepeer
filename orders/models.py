from django.db import models

# Create your models here.
from carts.models import Cart


class Order(models.model):
    order_id    = models.CharField(max_length=120)
    # billing_profile =
    # shipping_address =
    # billing_address =
    cart = models.ForeignKey(Cart)
    status = model.CharField(max_length=120, default='created')