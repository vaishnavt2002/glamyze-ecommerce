from django.db import models

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    is_listed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.category_name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory_name = models.CharField(max_length=100)
    is_listed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.subcategory_name
    
class Product(models.Model):
    product_name = models.CharField(max_length=100)
    description = models.TextField()
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    image1 = models.ImageField(upload_to='product_images/')
    image2 = models.ImageField(upload_to='product_images/')
    image3 = models.ImageField(upload_to='product_images/')
    is_listed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    material = models.CharField(max_length=50)
    color = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.product_name

class Size(models.Model):
    size_name = models.CharField(max_length=20)
    size_code = models.CharField(max_length=10)

    def __str__(self):
        return self.size_name
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    quantity = models.IntegerField(default=0)
    is_listed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'size']

    def __str__(self):
        return f"{self.product.product_name} - {self.size.size_name}"