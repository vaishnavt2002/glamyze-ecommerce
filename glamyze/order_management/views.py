from django.shortcuts import render
from order_app.models import *
from django.core.paginator import Paginator
from django.urls import reverse

def order_view(request):
    if request.user.is_superuser:
        searchvalue = request.GET.get('searchvalue', '')
        orders = Order.objects.all().order_by('-id')
        if searchvalue:
            orders = orders.filter(user__email__icontains=searchvalue)
        paginator = Paginator(orders, 10)
        page_number = request.GET.get('page')
        orders_page = paginator.get_page(page_number)
        return render(request, 'my_admin/orders.html', {'orders': orders_page,'searchvalue': searchvalue,})
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    


def order_detail(request,order_id):
    if request.user.is_superuser:
        order = Order.objects.get(id=order_id)
        return render(request,'my_admin/order_detail.html',{'order':order})
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    

def order_update(request,order_id):
    if request.user.is_superuser:
        if request.POST:
            order = Order.objects.get(id=order_id)
            status = request.POST.get('order_status')
            order.order_status = status
            order.save()
        return render(request,'my_admin/alert.html',{'order_update':True,'order_id':order_id})
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    


