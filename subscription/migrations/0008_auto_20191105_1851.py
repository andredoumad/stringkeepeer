# Generated by Django 2.2.6 on 2019-11-05 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0007_auto_20191105_1849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='slug',
            field=models.SlugField(blank=True),
        ),
    ]
