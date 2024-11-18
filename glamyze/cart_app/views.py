from django.shortcuts import render,redirect,get_object_or_404
from product_app.models import *
from django.views.decorators.cache import never_cache
from . models import *
from django.utils import timezone
from django.views.decorators.cache import never_cache




# Create your views here.
@never_cache
def add_to_cart(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
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

            if variant.quantity < int(num_product):
                variant = ProductVariant.objects.get(id=variant_id)
                product = Product.objects.get(id=variant.product.id)
                print(variant.size.id)
                return render(request,'user/product_view.html',{'product':product,'size_id':variant.size.id,'noquantity':True})
            if  5 < int(num_product):
                variant = ProductVariant.objects.get(id=variant_id)
                product = Product.objects.get(id=variant.product.id)
                return render(request,'user/product_view.html',{'product':product,'size_id':variant.size.id,'maxquantity':True})
            if  0 == int(num_product):
                variant = ProductVariant.objects.get(id=variant_id)
                product = Product.objects.get(id=variant.product.id)
                return render(request,'user/product_view.html',{'product':product,'size_id':variant.size.id,'minquantity':True})
            

               
            product = variant.product 
            try:
                cart = Cart.objects.get(user_id=request.user.id)
            except Exception:
                cart = Cart(user_id=request.user.id)
                cart.save()
                cart.refresh_from_db()


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
    
@never_cache
def cart_view(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        context={}
        if request.POST:
            num_products = request.POST.get('num_product')
            item_id = request.POST.get('item_id')
            cart_item = CartItem.objects.get(id=item_id)
            variant = ProductVariant.objects.get(id=cart_item.productvariant_id)
            if int(num_products) < cart_item.quantity:
                cart_item.quantity=int(num_products)
                cart_item.save()
            elif int(num_products) > cart_item.quantity:
                if int(num_products) > variant.quantity:
                    context = {'quantity_error' : True}
                elif int(num_products) > 5:
                    context = {'max_quantity_error' : True}
                else:
                    cart_item.quantity=int(num_products)
                cart_item.save()
        
        user_id = request.user.id
        cart, created = Cart.objects.get_or_create(user_id=user_id)
        cart_items = CartItem.objects.filter(cart=cart).order_by('id')
        total_price = 0
        
        for item in cart_items:
            original_price = float(item.productvariant.price)
            current_date = timezone.now().date()
            if item.productvariant.product.offer and item.productvariant.product.offer.is_active and item.productvariant.product.offer.start_date<=current_date and item.productvariant.product.offer.end_date>=current_date:
                discount = float(item.productvariant.product.offer.discount_percentage)
                offer_price = original_price - (original_price * (discount / 100))
                item.offer_price = round(offer_price, 2)
                item.total_price = item.offer_price * item.quantity
            else:
                item.offer_price = None
                item.total_price = original_price * item.quantity
            
            total_price += item.total_price
            
            if not item.productvariant.is_listed or not item.productvariant.product.is_active or not item.productvariant.product.is_listed or not item.productvariant.product.subcategory.is_listed or not item.productvariant.product.subcategory.category.is_listed:
                item.not_listed = True
            elif item.productvariant.quantity == 0:
                item.remove = True
            elif item.quantity > item.productvariant.quantity:
                item.warning = True
        
        context.update({
            'cart_items': cart_items,
            'total_price': round(total_price, 2)
        })
        return render(request, 'user/cart.html', context)
    else:
        return redirect('auth_app:login')
    
def cart_item_delete(request,id):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    if request.user.is_authenticated:
            if request.user.is_block:
                return redirect('auth_app:logout')
            CartItem.objects.get(id=id).delete()
            return redirect('cart_app:cart_view')
    else:
        return redirect('auth_app:login')



