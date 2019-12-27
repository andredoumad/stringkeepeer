from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager
)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, is_staff=False, is_admin=False):
        
        if not email:
            raise ValueError("users must of an email address")
        if not password:
            raise ValueError("Users mus have a password")

        user = self.model(
            email = self.normalize_email(email)
        )

        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.save(using=self._db)
        return user

    def create_staffuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
            is_staff=True
        )
        return user


    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user



class User(AbstractBaseUser):
    #identity
    email   = models.EmailField(max_length=255, unique=True)
    # full_name = models.CharField(max_length=255, blank=True, null=True)

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
        
    ] 

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

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