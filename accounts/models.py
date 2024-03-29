
import datetime 
import os
import random
import string

from django.utils import timezone
from django.utils.text import slugify

from datetime import timedelta
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager
)
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import get_template
from stringkeeper.standalone_tools import * 


# sendmail(subject, message, from_email, recipient_list, html_message)



DEFAULT_ACTIVATION_DAYS = getattr(settings, 'DEFAULT_ACTIVATION_DAYS', 7)

class UserManager(BaseUserManager):

    def create_user(self, email=None, password=None, is_active=False, last_name=None, first_name=None, full_name=None, is_staff=False, is_admin=False, user_id=None):
        
        if not email:
            raise ValueError("users must have a valid email address")

        if not password:
            raise ValueError("Users must have a password")

        if not first_name:
            raise ValueError("Users must have a first name")

        if not last_name:
            raise ValueError("Users must have a last name")

        user_obj = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            full_name = str(str(first_name) + ' ' + str(last_name)),
            user_id = str(str(first_name) + str(''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(15))) + str(last_name))
        )

        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.is_active = is_active
        user_obj.save(using=self._db)

        return user_obj

    def create_staffuser(self, email=None, password=None, last_name=None, first_name=None):
        user = self.create_user(
            email=email,
            password = password,
            first_name = first_name,
            last_name = last_name,
            full_name = str(str(first_name) + ' ' + str(last_name)),
            user_id = str(str(first_name) + str(''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(15))) + str(last_name)),
            is_staff = True

        )
        return user


    def create_superuser(self, email=None, password=None, last_name=None, first_name=None):
        user = self.create_user(
            email=email,
            password = password,
            first_name = first_name,
            last_name = last_name,
            full_name = str(str(first_name) + ' ' + str(last_name)),
            user_id = str(str(first_name) + str(''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(15))) + str(last_name)),
            is_staff = True,
            is_admin = True,
            is_active = True
        )
        return user



class User(AbstractBaseUser):
    #identity
    email   = models.EmailField(max_length=255, unique=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=127, blank=True, null=True)
    last_name = models.CharField(max_length=127, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    staff   = models.BooleanField(default=False)
    admin   = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    bool_webharvest_chat_active = models.BooleanField(default=False)
    bool_webharvest_robot_assigned = models.BooleanField(default=False)
    webharvest_robot_name = models.CharField(max_length=255, blank=True, null=True)
    bool_temporary_user = models.BooleanField(default=False)
    temporary_user_ip = models.CharField(max_length=255, blank=True, null=True)


    geo_ip_organization_name    = models.CharField(max_length=255, blank=True, null=True)
    geo_ip_region               = models.CharField(max_length=255, blank=True, null=True)
    geo_ip_accuracy             = models.CharField(max_length=255, blank=True, null=True)
    geo_ip_organization         = models.CharField(max_length=255, blank=True, null=True)
    geo_ip_timezone             = models.CharField(max_length=255, blank=True, null=True)
    geo_ip_longitude            = models.CharField(max_length=255, blank=True, null=True)
    geo_ip_country_code3        = models.CharField(max_length=255, blank=True, null=True)
    geo_ip_area_code            = models.CharField(max_length=255, blank=True, null=True)
    geo_ip_ip                   = models.CharField(max_length=255, blank=True, null=True)
    geo_ip_city                 = models.CharField(max_length=255, blank=True, null=True)
    geo_ip_country              = models.CharField(max_length=255, blank=True, null=True)
    geo_ip_continent_code       = models.CharField(max_length=255, blank=True, null=True)
    geo_ip_country_code         = models.CharField(max_length=255, blank=True, null=True)
    geo_ip_latitude             = models.CharField(max_length=255, blank=True, null=True)
    


    # confirmed_bool = models.BooleanField(default=False)

    #dates
    # confirmed_date = models.DateTimeField(default=False)
    # created_date = models.DateTimeField(auto_now_add=True)
    # activity_date = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    #email and password are required by default
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        
    ] 

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_full_name(self):
        return self.full_name

    def get_user_id(self):
        return self.user_id

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        if self.is_admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin




class EmailActivationQuerySet(models.query.QuerySet): 
    def confirmable(self):
        now = timezone.now()
        start_range = now - timedelta(days=DEFAULT_ACTIVATION_DAYS)
        # does my object have a timestamp in here
        end_range = now
        return self.filter(
                activated = False,
                forced_expired = False
              ).filter(
                #__gt = greater than
                timestamp__gt=start_range,
                # __lte = less than or equal to
                timestamp__lte=end_range
              )



class EmailActivationManager(models.Manager):
    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using=self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()

    def email_exists(self, email):
        return self.get_queryset().filter(
                    Q(email=email) | 
                    Q(user__email=email)
                ).filter(
                    activated=False
                )


class EmailActivation(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    email = models.EmailField()
    key = models.CharField(max_length=120, blank=True, null=True)
    activated = models.BooleanField(default=False)
    forced_expired = models.BooleanField(default=False)
    expires = models.IntegerField(default=7) #7 days
    timestamp = models.DateTimeField(auto_now_add=True) 
    update = models.DateTimeField(auto_now_add=True)

    objects = EmailActivationManager()

    def __str__(self):
        return self.email


    def can_activate(self):
        qs = EmailActivation.objects.filter(pk=self.pk).confirmable() # 1 object
        if qs.exists():
            return True
        return False


    def activate(self):
        if self.can_activate():
            # think about adding:
            # pre activation user signal
            user = self.user
            email = self.email
            eventlog('self.user: ' + str(user))
            eventlog('self.email: ' + str(email))
            # eventlog('self.is_active: ' + str(self.is_active))
            user.is_active = True
            #   eventlog('self.is_active: ' + str(self.is_active))
            user.save()
            # think about adding:
            # post activation signal for user
            self.activated = True
            self.save()
            return True
        return False


    def regenerate(self): #regenerate the unique key
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False

    def send_activation(self):
        if not self.activated and not self.forced_expired:
            if self.key:
                # in case BASE_URL is missing -- use stringkeeper.com   
                base_url = getattr(settings, 'BASE_URL', 'https://www.stringkeeper.com/')
                key_path = reverse("account:email-activate", kwargs={'key': self.key})
                # key_path = self.key # use reverse
                path = "{base}{path}".format(base=base_url, path=key_path)
                eventlog(path)
                context = {
                    'path': path,
                    'email': self.email
                }
                key = random_string_generator(size=45)
                txt_ = get_template("registration/emails/verify.txt").render(context)
                html_ = get_template("registration/emails/verify.html").render(context)
                subject = 'Verify your email with stringkeeper to activate your account.'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [self.email]

                sent_mail = send_mail(
                    subject, 
                    txt_, 
                    from_email, 
                    recipient_list, 
                    html_message = html_, 
                    fail_silently=False
                )
                return sent_mail
        return False


def pre_save_email_activation(sender, instance, *args, **kwargs):
    if not instance.activated and not instance.forced_expired:
        if not instance.key:
            instance.key = unique_key_generator(instance)

pre_save.connect(pre_save_email_activation, sender=EmailActivation)


def post_save_user_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        if instance.last_name != 'temporaryuser':
            eventlog('SENDING USER ACTIVATION!')
            obj = EmailActivation.objects.create(user=instance, email=instance.email)
            obj.send_activation()

post_save.connect(post_save_user_create_receiver, sender=User)



class GuestEmail(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email



def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_key_generator(instance):
    """
    This is for a Django project with an key field
    """
    size = random.randint(30, 45)
    key = random_string_generator(size=size)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(key=key).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return key


def generate_user_id():
    user_id = random_string_generator(size=20)
    matching_id = None
    matching_id = User.objects.filter(user_id=user_id)
    if matching_id != None:
        return generate_user_id()
    return user_id


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=4)
                )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug