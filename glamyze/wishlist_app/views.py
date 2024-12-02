from django.shortcuts import render,redirect
from django.views.decorators.cache import never_cache
from .models import *
from cart_app.models import *


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
        return render(request,'user/wishlist.html',{'wishlist_items':wishlist_items})        
    else:
        return redirect('auth_app:login')
    
@never_cache
def add_to_wishlist(request,productvariant_id):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        if Wishlist.objects.filter(user=request.user).exists():
            wishlist = Wishlist.objects.get(user=request.user)
        else:
            wishlist = Wishlist.objects.create(user=request.user)
        if not WishlistItem.objects.filter(wishlist=wishlist,productvariant_id=productvariant_id):
            wishlist_obj = WishlistItem(productvariant_id=productvariant_id,wishlist=wishlist)
            wishlist_obj.save()
        productvariant = ProductVariant.objects.get(id=productvariant_id)
        return redirect('product_app:product_view', product_id=productvariant.product_id)        
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
    
@never_cache
def add_to_cart(request,wishlistitem_id):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        wishlistitem = WishlistItem.objects.get(id=wishlistitem_id)
        try:
            variant = ProductVariant.objects.get(
                id=wishlistitem.productvariant_id,
                is_listed=True,
                product__is_active=True,
                product__is_listed=True,
                product__subcategory__is_listed=True,
                product__subcategory__category__is_listed=True
            )
        except:
            return render(request, 'user/alert.html',{'notsuccess':True})

        if variant.quantity == 0:
            return render(request,'user/alert.html',{'noquantity':True})
    
        try:
            cart = Cart.objects.get(user_id=request.user.id)
        except Exception:
            cart = Cart(user_id=request.user.id)
            cart.save()
            cart.refresh_from_db()


        try:
            cart_item = CartItem.objects.get(cart=cart,productvariant_id=variant.id)
            cart_item.quantity = 1
            cart_item.save()
        except Exception:
            cart_item = CartItem(cart=cart, productvariant_id=variant.id,quantity=1)
            cart_item.save()
        wishlistitem.delete()
        return render(request,'user/alert.html',{'wishlist_success':True})
    else:
        return redirect('auth_app:login')

