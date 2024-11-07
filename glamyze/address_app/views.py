from django.shortcuts import render,redirect
from auth_app.models import *
# Create your views here.
def account_management(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    if request.user.is_block:
        return redirect('auth_app:logout')
    if request.user.is_authenticated:
        return render(request,'user/profile.html')
    else:
        return redirect('auth_app:login')
