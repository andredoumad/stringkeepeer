import random, os
from django.db import models
from stringkeeper.standalone_tools import *
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.db.models import Q


from django.conf import settings
from django.core.files.storage import FileSystemStorage
from stringkeeper.aws.download.utils import AWSDownload
from stringkeeper.aws.utils import ProtectedS3Storage
from stringkeeper.utils import unique_slug_generator, get_filename

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


class SubscriptionQuerySet(models.query.QuerySet):
    
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)

    def search(self, query):
        eventlog(query)
        lookups = (
            Q(title__icontains=query) | 
            Q(description__icontains=query) | 
            Q(price__icontains=query)|
            Q(tag__title__icontains=query)
            )
        # tshirt, t-shirt, t shirt
        return self.filter(lookups).distinct()


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
    
    def search(self, query):
        return self.get_queryset().active().search(query)


class Subscription(models.Model): 
    title           = models.CharField(max_length=120)
    slug            = models.SlugField(blank=True, unique=True)
    description     = models.TextField()
    price           = models.DecimalField(max_digits=20,  decimal_places=2)
    image           = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    featured        = models.BooleanField(default=False)
    active          = models.BooleanField(default=True)
    timestamp       = models.DateTimeField(auto_now_add=True)
    is_digital      = models.BooleanField(default=True) # User Library

    objects = SubscriptionManager()
    
    def get_absolute_url(self):
        #return "/subscriptions/{slug}/".format(slug=self.slug)
        return reverse("subscription:detail", kwargs={"slug": self.slug})

    #this will show the overriding the 'class name' by the title string
    def __str__(self):
        if self.title != None:
            return self.title
        else:
            return str('deleted subscription')

    @property
    def name(self):
        return self.title

    def get_downloads(self):
        qs = self.subscriptionfile_set.all()
        return qs

def subscription_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(subscription_pre_save_receiver, sender=Subscription)



def upload_subscription_file_loc(instance, filename):
    slug = instance.subscription.slug
    #id_ = 0
    id_ = instance.id
    if id_ is None:
        Klass = instance.__class__
        qs = Klass.objects.all().order_by('-pk')
        if qs.exists():
            id_ = qs.first().id + 1
        else:
            id_ = 0
    if not slug:
        slug = unique_slug_generator(instance.subscription)
    location = "subscription/{slug}/{id}/".format(slug=slug, id=id_)
    return location + filename #"path/to/filename.mp4"



class SubscriptionFile(models.Model):
    subscription         = models.ForeignKey(Subscription, null=True, on_delete=models.SET_NULL)
    name            = models.CharField(max_length=120, null=True, blank=True)
    file            = models.FileField(
                        upload_to=upload_subscription_file_loc, 
                        storage=ProtectedS3Storage(), #FileSystemStorage(location=settings.PROTECTED_ROOT)
                        ) # path
    #filepath        = models.TextField() # '/protected/path/to/the/file/myfile.mp3'
    free            = models.BooleanField(default=False) # purchase required
    user_required   = models.BooleanField(default=False) # user doesn't matter


    def __str__(self):
        return str(self.file.name)

    @property
    def display_name(self):
        og_name = get_filename(self.file.name)
        if self.name:
            return self.name
        return og_name

    def get_default_url(self):
        return self.subscription.get_absolute_url()

    def generate_download_url(self):
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        region = getattr(settings, 'AWS_S3_REGION_NAME')
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        if not secret_key or not access_key or not bucket or not region:
            return "/subscription-not-found/"
        PROTECTED_DIR_NAME = getattr(settings, 'PROTECTED_DIR_NAME', 'protected')
        path = "{base}/{file_path}".format(base=PROTECTED_DIR_NAME, file_path=str(self.file))
        aws_dl_object =  AWSDownload(access_key, secret_key, bucket, region)
        file_url = aws_dl_object.generate_url(path, new_filename=self.display_name)
        return file_url

    def get_download_url(self): # detail view
        return reverse("subscription:download", 
                    kwargs={"slug": self.subscription.slug, "pk": self.pk}
                )
