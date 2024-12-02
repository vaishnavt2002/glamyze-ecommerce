from django.db import models
from auth_app.models import *
from product_app.models import *
# Create your models here.
class Wishlist(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist,on_delete=models.CASCADE)
    productvariant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE,default=None,null=True)
    created_at = models.DateTimeField(auto_now_add=True)