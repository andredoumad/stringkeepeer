# Generated by Django 2.2.6 on 2020-01-20 04:10

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0020_remove_billingprofile_braintree_subscription_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingprofile',
            name='braintree_subscriptions',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), default=list, size=None),
        ),
    ]
