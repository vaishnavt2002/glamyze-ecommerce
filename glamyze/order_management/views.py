from django.shortcuts import render,redirect
from order_app.models import *
from django.core.paginator import Paginator
from django.urls import reverse
from wallet_app.models import *
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q


def order_view(request):
    if request.user.is_superuser:
        searchvalue = request.GET.get('searchvalue', '')
        orders = Order.objects.exclude(order_status='PENDING').order_by('-id')
        if searchvalue:
            orders = orders.filter(user__email__icontains=searchvalue)
        for order in orders:
            order.has_pending_return = order.orderitem_set.filter(orderreturn__status='REQUESTED').exists()
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
        has_return = order.orderitem_set.filter(Q(orderreturn__status='REQUESTED')|Q(orderreturn__status='APPROVED')|Q(orderreturn__status='REJECTED')).exists()
        return render(request,'my_admin/order_detail.html',{'order':order,'has_return':has_return})
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
            if order.order_status == 'DELIVERED':
                order.delivery_date = timezone.now()
            if order.payment_method == 'cod':
                order.payment_status = 'PAID'
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
        cancellation_data = OrderCancellation(order = order,reason_type='Cancelled by admin',cancelled_by='ADMIN')
        
        cancellation_data.save()
        order.order_status = 'CANCELLED'
        order.payment_status = 'REFUNDED'
        order.save()
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            item.product_variant.quantity += item.quantity
            item.product_variant.save()
        if order.payment_method == 'razorpay' or order.payment_method == 'wallet':
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
    
def order_return_approve(request,orderitem_id):

    if request.user.is_superuser:
        try:
            order_item = OrderItem.objects.get(id=orderitem_id)
        except:
            return redirect('order_management:order_view')
        if order_item.offer_applied:
            refund_amount = order_item.offer_price * order_item.quantity
        else:
            refund_amount = order_item.price * order_item.quantity
        orderreturn = order_item.orderreturn
        order = order_item.order
        returned_items_total = sum(item.total_price for item in OrderItem.objects.filter(order=order,orderreturn__status='APPROVED'))
        total =order.get_subtotal()-order.get_offer_discount()
        if returned_items_total:
            total -= returned_items_total
        if order.coupon:
                if order.coupon.mininum_order_amount < total:
                    new_total = order.get_subtotal() - (order_item.price * order_item.quantity) - order.get_offer_discount()
                    if new_total < order.coupon.mininum_order_amount:
                        refund_amount -= order.coupon.discount_amount
                    if refund_amount < 0:
                        refund_amount = 0
        orderreturn.status = 'APPROVED'
        orderreturn.save()
        order_items = OrderItem.objects.filter(order=order)
        delivery_refund = True
        for item in order_items:
            try:
                if item.orderreturn.status == 'REJECTED' or item.orderreturn.status == 'REQUESTED':
                    delivery_refund = False
                    break
            except:
                delivery_refund = False
                break
        if delivery_refund:
            refund_amount += 40
                
        wallet, created = Wallet.objects.get_or_create(user=order.user)
        if refund_amount > 0:
            wallet.balance += refund_amount
            wallet.save() 
        WalletTransaction.objects.create(wallet=wallet,transaction_type='REFUND',amount=refund_amount)
        
        return redirect('order_management:order_detail', order_id = order_item.order_id)
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
def order_return_reject(request,orderitem_id):
    if request.user.is_superuser:
        try:
            order_item = OrderItem.objects.get(id=orderitem_id)
        except:
            return redirect('order_management:order_view')
        orderreturn = order_item.orderreturn
        orderreturn.status = 'REJECTED'
        orderreturn.save()
        return redirect('order_management:order_detail', order_id = order_item.order_id)
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')

    


