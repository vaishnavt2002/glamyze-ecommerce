# Generated by Django 5.1.2 on 2024-11-21 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0003_orderitem_offer_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='razorpay_payment_signature',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]