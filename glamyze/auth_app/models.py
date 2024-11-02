from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth import logout
from django.shortcuts import redirect
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_block = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']



@receiver(user_logged_in)
def check_if_user_is_blocked(sender, request, user, **kwargs):
    if user.is_block:
        logout(request)
        return redirect('auth_app:login')
