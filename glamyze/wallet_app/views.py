from django.shortcuts import render
from django.views.decorators.cache import never_cache
from .models import *
import razorpay
from django.conf import settings


# Create your views here.
@never_cache
def wallet_view(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        if Wallet.objects.filter(user=request.user).exists():
            wallet = Wallet.objects.get(user=request.user)
        else:
            wallet = Wallet.objects.create(user=request.user)
        transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-id')
        return render(request,'user/wallet.html',{'transactions':transactions,'wallet':wallet})        
    else:
        return redirect('auth_app:login')
    
def add_amount(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        if request.POST:
            wallet,created = Wallet.objects.get_or_create(user=request.user)
            amount = request.POST.get('amount')
            client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID,settings.KEY_SECRET))
            payment = client.order.create({'amount' : int(float(amount)*100), 'currency':'INR','payment_capture':1})
            print(payment)
            context = {'payment':payment,'key':settings.RAZOR_PAY_KEY_ID}
            WalletRazrorPay.objects.create(wallet=wallet,amount=amount,razorpay_order_id=payment['id'],status='PENDING')
            return render(request,'user/wallet_payment.html',context)      
    else:
        return redirect('auth_app:login')
    
def payment_success(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        if request.GET.get('payment_status') == 'success':
            payment_id= request.GET.get('payment_id')
            order_id = request.GET.get('order_id')
            signature = request.GET.get('signature')
            transacion = WalletRazrorPay.objects.get(razorpay_order_id=order_id)
            transacion.razorpay_payment_id = payment_id
            transacion.status = 'PAID'
            transacion.save()
            wallet = Wallet.objects.get(id=transacion.wallet_id)
            wallet.balance += transacion.amount
            wallet_transaction = WalletTransaction(wallet=wallet,transaction_type='CREDIT',amount=transacion.amount)
            wallet_transaction.save()
            wallet.save()
        return render(request,'user/alert.html',{'wallet_success':True})
        
    else:
        return redirect('auth_app:login')
    
def payment_failure(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        order_id = request.GET.get('order_id')
        transaction = WalletRazrorPay.objects.get(razorpay_order_id=order_id)
        transaction.status = 'FAILED'
        transaction.save()
        return render(request,'user/alert.html',{'wallet_failed':True})
        
    else:
        return redirect('auth_app:login')
    


