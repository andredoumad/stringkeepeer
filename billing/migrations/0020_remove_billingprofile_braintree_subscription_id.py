# Generated by Django 2.2.6 on 2020-01-20 03:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0019_delete_post'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billingprofile',
            name='braintree_subscription_id',
        ),
    ]
