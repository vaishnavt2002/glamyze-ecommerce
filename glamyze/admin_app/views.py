from django.shortcuts import render,redirect

# Create your views here.
def admin_home(request):
    if request.user.is_superuser:
        return render(request,'admin/dashboard.html')
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    