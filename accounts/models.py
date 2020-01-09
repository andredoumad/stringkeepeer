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
from django.utils import timezone
from stringkeeper.standalone_tools import * 
from stringkeeper.utils import random_string_generator, unique_key_generator

# sendmail(subject, message, from_email, recipient_list, html_message)



DEFAULT_ACTIVATION_DAYS = getattr(settings, 'DEFAULT_ACTIVATION_DAYS', 7)

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, is_active=True, last_name=None, first_name=None, full_name=None, is_staff=False, is_admin=False):
        
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
            full_name = str(str(first_name) + ' ' + str(last_name))
        )

        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.is_active = is_active
        user_obj.save(using=self._db)

        return user_obj

    def create_staffuser(self, email, password=None, last_name=None, first_name=None):
        user = self.create_user(
            email,
            password = password,
            first_name = first_name,
            last_name = last_name,
            full_name = str(str(first_name) + ' ' + str(last_name)),
            is_staff = True
        )
        return user


    def create_superuser(self, email, password=None, last_name=None, first_name=None):
        user = self.create_user(
            email,
            password = password,
            first_name = first_name,
            last_name = last_name,
            full_name = str(str(first_name) + ' ' + str(last_name)),
            is_staff = True,
            is_admin = True
        )
        return user



class User(AbstractBaseUser):
    #identity
    email   = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=127, blank=True, null=True)
    last_name = models.CharField(max_length=127, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    staff   = models.BooleanField(default=False)
    admin   = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
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

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
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
            print('self.user: ' + str(user))
            print('self.email: ' + str(email))
            # print('self.is_active: ' + str(self.is_active))
            user.is_active = True
            #   print('self.is_active: ' + str(self.is_active))
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


def post_save_user_create_reciever(sender, instance, created, *args, **kwargs):
    if created:
        obj = EmailActivation.objects.create(user=instance, email=instance.email)
        obj.send_activation()

post_save.connect(post_save_user_create_reciever, sender=User)



class GuestEmail(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email