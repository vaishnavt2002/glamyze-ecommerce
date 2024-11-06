from django.shortcuts import render,redirect,get_object_or_404
from product_app.models import *
from django.views.decorators.cache import never_cache
from . models import *


# Create your views here.
@never_cache
def add_to_cart(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    if request.user.is_block:
        return redirect('auth_app:logout')
    if request.user.is_authenticated:
        if request.GET:
            variant_id = request.GET['variant_id']
            num_product = request.GET['num_product']
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id,
                    is_listed=True,
                    product__is_active=True,
                    product__is_listed=True,
                    product__subcategory__is_listed=True,
                    product__subcategory__category__is_listed=True
                )
            except Exception:
                variant = ProductVariant.objects.get(id=variant_id)
                product = Product.objects.get(id=variant.product.id)
                return render(request,'user/product_view.html',{'product':product,'notsuccess':True})

                
                # At this point, all conditions are satisfied
            product = variant.product  # Retrieve the related product
            try:
                cart = Cart.objects.get(user_id=request.user.id)
            except Exception:
                cart = Cart(user_id=request.user.id)
                cart.save()
                cart.refresh_from_db()
            print(variant_id)
            print(num_product)
            try:
                cart_item = CartItem.objects.get(cart=cart,productvariant_id=variant_id)
                cart_item.quantity = num_product
                cart_item.save()
            except Exception:
                cart_item = CartItem(cart=cart, productvariant_id=variant_id,quantity=num_product)
                cart_item.save()
        return render(request,'user/product_view.html',{'product':product,'success':True})
    else:
        return redirect('auth_app:login')

def cart_view(request):
    return render(request,'user/cart.html')
