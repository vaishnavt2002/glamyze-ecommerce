from django.db import models
from auth_app.models import *
from product_app.models import *

# Create your models here.
class Cart(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Cart of user.email"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')  # Related to Cart
    productvariant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)  # The actual product in the cart
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self) -> str:
        return f"{self.quantity} of {self.productvariant.product.product_name}"
    
