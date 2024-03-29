# Generated by Django 2.2.6 on 2020-01-11 02:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0003_auto_20200110_0641'),
        ('orders', '0003_auto_20200111_0114'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shipping_address', to='addresses.Address'),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_total',
            field=models.DecimalField(decimal_places=2, default=5.99, max_digits=100),
        ),
    ]
