# Generated by Django 2.2.6 on 2020-01-13 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0011_auto_20200105_0327'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingprofile',
            name='braintree_customer_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]