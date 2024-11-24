from django.db import models
from auth_app.models import *
# Create your models here.

class Wallet(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}'s Wallet  "
    
class WalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('REFUND', 'Refund'),
        ('CANCELLATION','cancellation'),
        ('CREDIT','Credited'),
        ('DEBIT','Debited'),
        ('REFERRAL','Referral')
    ]

    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20,choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)