# Generated by Django 2.2.6 on 2019-11-05 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0005_auto_20191104_0608'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='featured',
            field=models.BooleanField(default=False),
        ),
    ]
