# Generated by Django 5.1.2 on 2024-11-04 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product_app", "0010_alter_productvariant_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productvariant",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]