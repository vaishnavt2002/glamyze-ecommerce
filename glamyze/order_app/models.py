from django.db import models
from auth_app.models import *
from address_app.models import *
from promotion_management.models import *
from product_app.models import *
# Create your models here.

class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED','Refunded')
    ]
    
    ORDER_STATUS_CHOICES = [
        ('FAILED','Failed'),
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('RETURNED', 'Returned')
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_signature = models.CharField(max_length=100, null=True, blank=True)
    coupon = models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True)
    delivery_date = models.DateTimeField(null=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_subtotal(self):
        subtotal=0
        for item in self.orderitem_set.all():
            subtotal += item.price * item.quantity
        return subtotal
    
    def get_offer_discount(self):
        offer_price = 0
        for item in self.orderitem_set.all():
            if item.offer_price is not None:
                offer_price += (item.price-item.offer_price) * item.quantity
        return offer_price


    def get_coupon_discount(self):
        return self.coupon.discount_amount if self.coupon else 0

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant,on_delete=models.SET_NULL,null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    offer_price = models.DecimalField(max_digits=10,decimal_places=2,null=True,default=None)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    offer_applied = models.ForeignKey(Offer,on_delete=models.SET_NULL,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class OrderAddress(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE)
    address = models.ForeignKey(Address,on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    pincode = models.CharField(max_length=10)
    locality = models.CharField(max_length=100)
    address_data = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100, blank=True, null=True)
    alternate_phone = models.CharField(max_length=15, blank=True, null=True)
    office_home = models.CharField(max_length=10)


class OrderCancellation(models.Model):
    CANCELLED_BY_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('ADMIN', 'Admin')
    ]   
    order = models.OneToOneField(Order,on_delete=models.CASCADE)
    reason_type = models.CharField(max_length=50)
    cancelled_date = models.DateTimeField(auto_now_add=True)
    cancelled_by = models.CharField(max_length=10, choices=CANCELLED_BY_CHOICES)

class OrderReturn(models.Model):
    RETURN_STATUS_CHOICES = [
        ('REQUESTED','requested'),
        ('APPROVED','approved'),
        ('REJECTED','Rejected')
    ]
    order_item = models.OneToOneField(OrderItem,on_delete=models.CASCADE)
    return_reason = models.CharField(max_length=20)
    return_explanation = models.TextField(null=True)
    status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

