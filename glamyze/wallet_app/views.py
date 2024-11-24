from django.shortcuts import render
from django.views.decorators.cache import never_cache
from .models import *


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
        transactions = WalletTransaction.objects.filter(wallet=wallet)
        return render(request,'user/wallet.html',{'transactions':transactions,'wallet':wallet})        
    else:
        return redirect('auth_app:login')