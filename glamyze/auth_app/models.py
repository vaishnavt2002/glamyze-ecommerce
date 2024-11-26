from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(null=True,max_length=13)
    is_block = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=20,null=True,unique=True)
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4().hex)[:8]
        super().save(*args, **kwargs)
    

    

