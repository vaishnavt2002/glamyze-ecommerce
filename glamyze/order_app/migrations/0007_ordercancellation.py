# Generated by Django 5.1.2 on 2024-11-23 09:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0006_alter_order_order_status_alter_order_payment_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderCancellation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason_type', models.CharField(max_length=50)),
                ('cancelled_date', models.DateTimeField(auto_now_add=True)),
                ('cancelled_by', models.CharField(choices=[('CUSTOMER', 'Customer'), ('ADMIN', 'Admin')], max_length=10)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='order_app.order')),
            ],
        ),
    ]