from django.shortcuts import render
from order_app.models import *
from django.core.paginator import Paginator
from django.urls import reverse
from wallet_app.models import *
from decimal import Decimal

def order_view(request):
    if request.user.is_superuser:
        searchvalue = request.GET.get('searchvalue', '')
        orders = Order.objects.exclude(order_status='PENDING').order_by('-id')
        for order in orders:
            try:
                if order.ordercancellation.status == "PENDING":
                    order.cancellation_request = True
                else:
                    order.cancellation_request = False
            except OrderCancellation.DoesNotExist:
                order.cancellation_request = False
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
        try:
            cancellation = OrderCancellation.objects.get(order=order)
        except:
            cancellation = None
        return render(request,'my_admin/order_detail.html',{'order':order,'cancellation':cancellation if cancellation.status == "PENDING" else None})
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
    
def order_cancellation(request,order_id):
    if request.user.is_superuser:
        try:
            order = Order.objects.get(id=order_id)
        except:
            return redirect('order_management:order_details',order_id=order_id)
        try:
            cancellation_data = OrderCancellation.objects.get(order=order)
        except:
            return redirect('order_management:order_details',order_id=order_id)
        if cancellation_data.status == 'PENDING':
            cancellation_data.status = "APPROVED"
            cancellation_data.save()
            order.order_status = 'CANCELLED'
            order.payment_status = 'REFUNDED'
            order.save()
            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                item.product_variant.quantity += item.quantity
                item.product_variant.save()
            if order.payment_method == 'razorpay':
                try:
                    wallet = Wallet.objects.get(user=order.user)
                except:
                    wallet = Wallet.objects.create(user=order.user)
                transaction = WalletTransaction.objects.create(wallet=wallet,transaction_type='CANCELLATION',amount=order.total_amount)
                wallet.balance += order.total_amount
                wallet.save()
            
            
        return redirect('order_management:order_detail',order_id=order.id)
        
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    


