from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
from .models import GuestEmail, EmailActivation
from .forms import UserAdminCreationForm, UserAdminChangeForm

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'geo_ip_country', 'geo_ip_city', 'admin')
    list_filter = ('admin', 'staff', 'is_active', 'bool_temporary_user')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': (
            'first_name',
            'last_name',
            'full_name',
            'user_id',
            'bool_webharvest_chat_active',
            'bool_webharvest_robot_assigned',
            'webharvest_robot_name',
            'bool_temporary_user',
            'temporary_user_ip',
            'geo_ip_organization_name',
            'geo_ip_region',
            'geo_ip_accuracy',
            'geo_ip_organization',
            'geo_ip_timezone',
            'geo_ip_longitude',
            'geo_ip_country_code3',
            'geo_ip_area_code',
            'geo_ip_ip',
            'geo_ip_city',
            'geo_ip_country',
            'geo_ip_continent_code',
            'geo_ip_country_code',
            'geo_ip_latitude'

            )}),
        ('Permissions', {'fields': ('admin', 'staff', 'is_active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = (
        'email', 
        'first_name',
        'last_name',
        'full_name',
        'user_id',
        'bool_webharvest_chat_active',
        'bool_webharvest_robot_assigned',
        'webharvest_robot_name',
        'bool_temporary_user',
        'temporary_user_ip',
        'geo_ip_organization_name',
        'geo_ip_region',
        'geo_ip_accuracy',
        'geo_ip_organization',
        'geo_ip_timezone',
        'geo_ip_longitude',
        'geo_ip_country_code3',
        'geo_ip_area_code',
        'geo_ip_ip',
        'geo_ip_city',
        'geo_ip_country',
        'geo_ip_continent_code',
        'geo_ip_country_code',
        'geo_ip_latitude'

    )
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)


# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)

class EmailActivationAdmin(admin.ModelAdmin):
    search_fields = ['email']
    class Meta:
        model = EmailActivation


admin.site.register(EmailActivation, EmailActivationAdmin)


class GuestEmailAdmin(admin.ModelAdmin):
    search_fields = ['email']
    class Meta:
        model = User

admin.site.register(GuestEmail, GuestEmailAdmin)