from django.shortcuts import render,redirect
from django.views.decorators.cache import never_cache


# Create your views here.
def admin_home(request):
    if request.user.is_superuser:
        return render(request,'my_admin/dashboard.html')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    