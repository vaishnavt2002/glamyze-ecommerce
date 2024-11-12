from django.db import models

# Create your models here.
class Banner(models.Model):
    class Type(models.TextChoices):
        HERO = 'HERO','Hero Banner'

    name = models.CharField(max_length=50)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='banner/')
    banner_type = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)