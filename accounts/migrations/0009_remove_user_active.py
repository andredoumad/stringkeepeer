# Generated by Django 2.2.6 on 2020-01-07 22:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_user_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='active',
        ),
    ]
