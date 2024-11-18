from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.db.models import Q
from auth_app.models import *
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache

# Create your views here.

@never_cache
def customer_details(request):
    if request.user.is_superuser:
        if request.method == "GET":
            search = request.GET.get('searchvalue', '')
            if search:
                customer_data = CustomUser.objects.filter(
                    Q(first_name__icontains=search) | Q(email__icontains=search)
                ).exclude(Q(is_superuser=1)|Q(is_active=0))
            else:
                customer_data = CustomUser.objects.exclude(Q(is_superuser=1)|Q(is_active=0))
            # Pagination
            paginator = Paginator(customer_data, 10) 
            page_number = request.GET.get('page', 1) 
            page_obj = paginator.get_page(page_number) 

        return render(request, 'my_admin/customer.html', {'customer_data': page_obj, 'searchvalue': search})
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')

    
    
@never_cache
def block_unblock_user(request, user_id):
    if request.user.is_superuser:
        if request.method == "POST":
            user_data = CustomUser.objects.get(id=user_id)
            user_data.is_block = not user_data.is_block
            user_data.save()
            return JsonResponse({'status': 'success', 'is_block': user_data.is_block})
        elif request.user.is_authenticated:
            if request.user.is_block:
                return redirect('auth_app:logout')
            return redirect('auth_app:home')
        else:
            return redirect('auth_app:login')
    return JsonResponse({'status': 'error'}, status=400)


