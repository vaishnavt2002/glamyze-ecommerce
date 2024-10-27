from django.shortcuts import render,redirect
from django.http import JsonResponse
from auth_app.models import *
# Create your views here.


def customer_details(request):
    if request.user.is_superuser:
        customer_data=CustomUser.objects.exclude(is_superuser=1)
        return render(request,'admin/customer.html',{'customer_data':customer_data})
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')

def block_unblock_user(request, user_id):
    if request.user.is_superuser:
        if request.method == "POST":
            user_data = CustomUser.objects.get(id=user_id)
            user_data.is_active = not user_data.is_active  # Toggle the active status
            user_data.save()
            return JsonResponse({'status': 'success', 'is_active': user_data.is_active})
        elif request.user.is_authenticated:
            return redirect('auth_app:home')
        else:
            return redirect('auth_app:login')
    return JsonResponse({'status': 'error'}, status=400)