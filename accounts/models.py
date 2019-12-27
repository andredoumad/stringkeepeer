from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager
)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, first_name=None, is_staff=False, is_admin=False):
        
        if not email:
            raise ValueError("users must of an email address")

        if not password:
            raise ValueError("Users must have a password")

        if not first_name:
            raise ValueError("Users must have a full name")

        user_obj = self.model(
            email = self.normalize_email(email),
            first_name = first_name
        )

        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin

        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, password=None, first_name=None):
        user = self.create_user(
            email,
            password = password,
            first_name = first_name,
            is_staff = True
        )
        return user


    def create_superuser(self, email, password=None, first_name=None):
        user = self.create_user(
            email,
            password = password,
            first_name = first_name,
            is_staff = True,
            is_admin = True
        )
        return user



class User(AbstractBaseUser):
    #identity
    email   = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)

    #
    active = models.BooleanField(default=True)
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
        'first_name'
        
    ] 

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_first_name(self):
        return self.first_name

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

    @property
    def is_active(self):
        return self.active

# # we may use this later
# class Profile(models.Model):
#     user = models.OneToOneField(User)
#     # extend extra data



class GuestEmail(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email