# Generated by Django 2.2.6 on 2019-11-12 23:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0009_auto_20191105_1959'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]