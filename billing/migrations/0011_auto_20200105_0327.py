# Generated by Django 2.2.6 on 2020-01-05 03:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0010_auto_20200103_2232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billingprofile',
            name='paypal_BillingAgreementToken',
        ),
        migrations.RemoveField(
            model_name='billingprofile',
            name='paypal_BillingPlan_id',
        ),
        migrations.RemoveField(
            model_name='billingprofile',
            name='paypal_CreditCard_id',
        ),
    ]