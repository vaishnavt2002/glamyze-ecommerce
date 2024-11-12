from django.db import models

# Create your models here.
class Offer(models.Model):
    offer_name = models.CharField(max_length=50)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=10,decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    

    def __str__(self) -> str:
        return self.offer_name