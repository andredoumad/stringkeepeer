# Generated by Django 2.2.6 on 2020-02-23 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webharvest', '0006_delete_webharvestmessagemodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebharvestJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_name', models.CharField(blank=True, max_length=255, null=True)),
                ('user_email', models.CharField(blank=True, max_length=255, null=True)),
                ('robot_name', models.CharField(blank=True, max_length=255, null=True)),
                ('somesetting', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
