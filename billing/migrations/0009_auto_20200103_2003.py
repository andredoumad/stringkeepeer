# Generated by Django 2.2.6 on 2020-01-03 20:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0008_auto_20200103_0629'),
    ]

    operations = [
        migrations.RenameField(
            model_name='card',
            old_name='number',
            new_name='last4',
        ),
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.CharField(max_length=120)),
                ('paid', models.BooleanField(default=False)),
                ('refunded', models.BooleanField(default=False)),
                ('outcome', models.TextField(blank=True, null=True)),
                ('outcome_type', models.CharField(blank=True, max_length=120, null=True)),
                ('seller_message', models.CharField(blank=True, max_length=120, null=True)),
                ('risk_level', models.CharField(blank=True, max_length=120, null=True)),
                ('billing_profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='billing.BillingProfile')),
            ],
        ),
    ]
