# Generated by Django 5.1.2 on 2024-11-12 10:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_app', '0012_productvariant_offer'),
        ('promotion_management', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productvariant',
            name='offer',
        ),
        migrations.AddField(
            model_name='product',
            name='offer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='promotion_management.offer'),
        ),
    ]
