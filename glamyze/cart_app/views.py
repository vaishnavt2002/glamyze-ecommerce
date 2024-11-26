from django.shortcuts import render,redirect,get_object_or_404
from product_app.models import *
from django.views.decorators.cache import never_cache
from . models import *
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
import json




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
        if request.session.get('coupon_code'):
            del request.session['coupon_code']
            

        context={}
       
        
        user_id = request.user.id
        cart, created = Cart.objects.get_or_create(user_id=user_id)
        cart_items = CartItem.objects.filter(cart=cart).order_by('id')
        total_price = 0
        
        for item in cart_items:
            original_price = float(item.productvariant.price)
            current_date = timezone.now().date()
            product_discount = 0
            category_discount = 0
            subcategory_discount = 0

            # Check for product-level offer
            if (item.productvariant.product.offer and item.productvariant.product.offer.is_active and 
                    item.productvariant.product.offer.start_date <= current_date <= item.productvariant.product.offer.end_date):
                product_discount = item.productvariant.price * (item.productvariant.product.offer.discount_percentage / 100)

            # Check for category-level offer
            if (item.productvariant.product.subcategory.category.offer and item.productvariant.product.subcategory.category.offer.is_active and 
                    item.productvariant.product.subcategory.category.offer.start_date <= current_date <= item.productvariant.product.subcategory.category.offer.end_date):
                category_discount = item.productvariant.price * (item.productvariant.product.subcategory.category.offer.discount_percentage / 100)

            # Check for subcategory-level offer
            if (item.productvariant.product.subcategory.offer and item.productvariant.product.subcategory.offer.is_active and 
                    item.productvariant.product.subcategory.offer.start_date <= current_date <= item.productvariant.product.subcategory.offer.end_date):
                subcategory_discount = item.productvariant.price * (item.productvariant.product.subcategory.offer.discount_percentage / 100)
            max_discount = max(product_discount, category_discount, subcategory_discount)

            # Apply the highest discount to the product price
            if max_discount > 0:
                item.offer_price = round(item.productvariant.price - max_discount, 2)
                item.total_price = item.offer_price * item.quantity
            else:
                item.offer_price = None
                item.total_price = original_price * item.quantity            
            total_price += float(item.total_price)
            if max_discount > 0:
                if max_discount == product_discount:
                    offer_applied = 'PRODUCT'
                elif max_discount == subcategory_discount:
                    offer_applied = 'SUBCATEGORY'
                elif max_discount == category_discount:
                    offer_applied = 'CATEGORY'
            else:
                offer_applied = None
            item.offer_applied = offer_applied
            
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
    

def cart_update(request,item_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        print(action)
        price = data.get('price')
        print(price)
        price=float(price)
        total_price =data.get('total_price')
        total_price=float(total_price)
        print(total_price)
        try:
            cart_item = CartItem.objects.get(id=item_id)
            variant = ProductVariant.objects.get(id=cart_item.productvariant_id)
            if cart_item.cart.user == request.user:
                if action == 'increase':
                    if cart_item.quantity + 1 > variant.quantity:
                        return JsonResponse({'status': 'error', 'message': 'No quantity to add.','new_quantity': cart_item.quantity})
                    elif cart_item.quantity + 1 > 5:
                        return JsonResponse({'status': 'error', 'message': 'Maximum allowed quantity is 5.','new_quantity': cart_item.quantity})
                    else:
                        cart_item.quantity += 1
                        total_price += price
                else:
                    if cart_item.quantity - 1 == 0:
                        pass
                    else:
                        cart_item.quantity -=1
                        total_price -= price
                cart_item.save()
                original_price = cart_item.productvariant.price
                return JsonResponse({
                'status': 'success',
                'new_quantity': cart_item.quantity,
                'price': price,
                'total_price':total_price,
                'original_price':original_price
                })
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found.','new_quantity': cart_item.quantity})
        
        




