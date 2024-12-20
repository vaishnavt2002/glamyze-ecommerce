# Generated by Django 5.1.2 on 2024-12-02 12:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_app', '0016_productreview'),
        ('wishlist_app', '0002_wishlistitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wishlistitem',
            name='product',
        ),
        migrations.AddField(
            model_name='wishlistitem',
            name='productvariant',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='product_app.productvariant'),
        ),
    ]
