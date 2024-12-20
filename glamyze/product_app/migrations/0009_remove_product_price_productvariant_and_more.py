# Generated by Django 5.1.2 on 2024-11-04 04:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product_app", "0008_alter_productsize_quantity"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="price",
        ),
        migrations.CreateModel(
            name="ProductVariant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("quantity", models.IntegerField(default=0)),
                ("is_listed", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="product_app.product",
                    ),
                ),
                (
                    "size",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="product_app.size",
                    ),
                ),
            ],
            options={
                "unique_together": {("product", "size")},
            },
        ),
        migrations.DeleteModel(
            name="ProductSize",
        ),
    ]
