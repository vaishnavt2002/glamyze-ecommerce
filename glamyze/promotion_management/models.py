from django.db import models

# Create your models here.
class Offer(models.Model):
    OFFER_TYPE_CHOICES = [
        ('PRODUCT', 'Product Offer'),
        ('CATEGORY', 'Category Offer'),
        ('SUBCATEGORY', 'Subcategory Offer')
    ]
    offer_name = models.CharField(max_length=50)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=10,decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    offer_type = models.CharField(max_length=30,choices=OFFER_TYPE_CHOICES, default='CATEGORY')
    is_active = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.offer_name
    
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    mininum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    maximum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    usage_limit = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField()
    discount_amount = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self) -> str:
        return self.code
