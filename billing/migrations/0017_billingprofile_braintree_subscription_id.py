# Generated by Django 2.2.6 on 2020-01-17 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0016_auto_20200117_0150'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingprofile',
            name='braintree_subscription_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]