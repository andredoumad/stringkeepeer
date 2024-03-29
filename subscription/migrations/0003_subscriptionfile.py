# Generated by Django 2.2.6 on 2020-01-11 22:38

from django.db import migrations, models
import django.db.models.deletion
import storages.backends.s3boto3
import subscription.models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_subscription_is_digital'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=120, null=True)),
                ('file', models.FileField(storage=storages.backends.s3boto3.S3Boto3Storage(location='protected'), upload_to=subscription.models.upload_subscription_file_loc)),
                ('free', models.BooleanField(default=False)),
                ('user_required', models.BooleanField(default=False)),
                ('subscription', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='subscription.Subscription')),
            ],
        ),
    ]
