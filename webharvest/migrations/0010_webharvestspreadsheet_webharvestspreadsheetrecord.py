# Generated by Django 2.2.6 on 2020-04-07 05:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webharvest', '0009_webharvestthread_message_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebharvestSpreadSheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_count', models.IntegerField(blank=True, null=True)),
                ('filepath', models.CharField(blank=True, max_length=255, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('thread', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webharvest.WebharvestThread')),
            ],
        ),
        migrations.CreateModel(
            name='WebharvestSpreadSheetRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField(blank=True, null=True)),
                ('url', models.TextField(blank=True, null=True)),
                ('sentence', models.TextField(blank=True, null=True)),
                ('noun_chunk', models.TextField(blank=True, null=True)),
                ('lemma', models.TextField(blank=True, null=True)),
                ('pos', models.CharField(blank=True, max_length=32, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('label', models.CharField(blank=True, max_length=64, null=True)),
                ('spreadsheet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webharvest.WebharvestSpreadSheet')),
            ],
        ),
    ]
