# Generated by Django 2.2.6 on 2020-01-03 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0005_auto_20200102_2220'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingprofile',
            name='paypal_BillingPlan_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='billingprofile',
            name='paypal_CreditCard_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='billingprofile',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
