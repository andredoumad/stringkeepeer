from django.db import models

# Create your models here.
class Subscription(models.Model): 
    title           = models.CharField(max_length=120)
    description     = models.TextField()
    price           = models.DecimalField(max_digits=20,  decimal_places=2)
    image           = models.FileField(upload_to='subscription/', null=True, blank=True)

    #this will show the overriding the 'class name' by the title string
    def __str__(self):
        return self.title