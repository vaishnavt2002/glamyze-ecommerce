from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.db.models import Q
from auth_app.models import *
from django.core.paginator import Paginator
# Create your views here.

def customer_details(request):
    if request.user.is_superuser:
        if request.method == "GET":
            search = request.GET.get('searchvalue', '')
            if search:
                customer_data = CustomUser.objects.filter(
                    Q(first_name__icontains=search) | Q(email__icontains=search)
                ).exclude(is_superuser=1)
            else:
                customer_data = CustomUser.objects.exclude(is_superuser=1)
            # Pagination
            paginator = Paginator(customer_data, 10)  # Show 10 customers per page
            page_number = request.GET.get('page', 1)  # Get the page number from the request, default to 1
            page_obj = paginator.get_page(page_number)  # Get the specific page

        return render(request, 'admin/customer.html', {'customer_data': page_obj, 'searchvalue': search})
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')

    
    
#this function will produce Json Response. This is for the AJAX request coming.
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


