# Generated by Django 5.1.2 on 2024-11-12 09:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_app', '0011_alter_productvariant_price'),
        ('promotion_management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='offer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='promotion_management.offer'),
        ),
    ]
