# Generated by Django 2.2.6 on 2020-02-14 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_auto_20200207_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='channel_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]