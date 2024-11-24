from django.shortcuts import render,redirect
from django.views.decorators.cache import never_cache
from .models import *


# Create your views here.
@never_cache
def wishlist_view(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        wishlist_items = None
        if Wishlist.objects.filter(user=request.user).exists():
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
            for item in wishlist_items:
                obj =item.product.productvariant_set.first()
                item.product.price = obj.price

        return render(request,'user/wishlist.html',{'wishlist_items':wishlist_items})        
    else:
        return redirect('auth_app:login')
    
@never_cache
def add_to_wishlist(request,product_id):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        if Wishlist.objects.filter(user=request.user).exists():
            wishlist = Wishlist.objects.get(user=request.user)
        else:
            wishlist = Wishlist.objects.create(user=request.user)
        if not WishlistItem.objects.filter(wishlist=wishlist,product_id=product_id):
            wishlist_obj = WishlistItem(product_id=product_id,wishlist=wishlist)
            wishlist_obj.save()
        
        return redirect('product_app:product_view', product_id=product_id)        
    else:
        return redirect('auth_app:login')
    
@never_cache
def delete_from_wishlist(request,wishlistitem_id):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        if WishlistItem.objects.filter(id=wishlistitem_id).exists():
            item = WishlistItem.objects.get(id=wishlistitem_id)
            if item.wishlist.user == request.user:
                item.delete()
            else:
                return redirect('auth_app:logout')
        
        return redirect('wishlist_app:wishlist_view')        
    else:
        return redirect('auth_app:login')

