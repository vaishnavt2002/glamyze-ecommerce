from django.shortcuts import render
from address_app.models import *
from cart_app.models import *
from django.urls import reverse

# Create your views here.
def proceed_to_checkout(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        context={}
        user_id = request.user.id
        cart = Cart.objects.get(user_id=user_id)
        cart_items = CartItem.objects.filter(cart=cart).select_related('cart')
        total_price = 0
        change = False
        for item in cart_items:
            original_price = float(item.productvariant.price)
            # Calculate offer price if offer exists
            if item.productvariant.product.offer:
                discount = float(item.productvariant.product.offer.discount_percentage)
                offer_price = original_price - (original_price * (discount / 100))
                item.offer_price = round(offer_price, 2)
                item.total_price = item.offer_price * item.quantity
            else:
                item.offer_price = None
                item.total_price = original_price * item.quantity
            
            total_price += item.total_price
            
            if not item.productvariant.is_listed or not item.productvariant.product.is_active or not item.productvariant.product.is_listed or not item.productvariant.product.subcategory.is_listed or not item.productvariant.product.subcategory.category.is_listed:
                change = True
            elif item.productvariant.quantity == 0:
                change = True
            elif item.quantity > item.productvariant.quantity:
                change = True
        if change:
            context['change'] =True
            context.update({
                        'cart_items': cart_items,
                        'total_price': round(total_price, 2),
                    })
            return render(request, 'user/cart.html', context)
                
        else:
            return redirect('order_app:checkout_view')
    else:
        return redirect('auth_app:login')


def checkout_view(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        
        change = False
        addresses = Address.objects.filter(user=request.user)
        context={}
        user_id = request.user.id
        cart = Cart.objects.get(user_id=user_id)
        cart_items = CartItem.objects.filter(cart=cart).select_related('cart')
        total_price = 0
        
        for item in cart_items:
            original_price = float(item.productvariant.price)
            # Calculate offer price if offer exists
            if item.productvariant.product.offer:
                discount = float(item.productvariant.product.offer.discount_percentage)
                offer_price = original_price - (original_price * (discount / 100))
                item.offer_price = round(offer_price, 2)
                item.total_price = item.offer_price * item.quantity
            else:
                item.offer_price = None
                item.total_price = original_price * item.quantity
            
            total_price += item.total_price
            if not item.productvariant.is_listed or not item.productvariant.product.is_active or not item.productvariant.product.is_listed or not item.productvariant.product.subcategory.is_listed or not item.productvariant.product.subcategory.category.is_listed:
                change = True
            elif item.productvariant.quantity == 0:
                change = True
            elif item.quantity > item.productvariant.quantity:
                change = True

        if request.POST:
            selected_address = request.POST.get('selected_address')
            payment_method = request.POST.get('payment_method')
            if not change:
                url = reverse('order_app:order_summary')
                query_string = f'?address={selected_address}&payment={payment_method}'
    
                return redirect(f"{url}{query_string}")
            else:
                context['change']=True
        context.update({
            'cart_items': cart_items,
            'total_price': round(total_price, 2),
            'addresses' : addresses
        })
        return render(request, 'user/checkout.html', context)
    else:
        return redirect('auth_app:login')
    

def order_summary(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        change = False
        addresses = Address.objects.filter(user=request.user)
        context={}
        user_id = request.user.id
        cart = Cart.objects.get(user_id=user_id)
        cart_items = CartItem.objects.filter(cart=cart).select_related('cart')
        total_price = 0
        
        for item in cart_items:
            original_price = float(item.productvariant.price)
            # Calculate offer price if offer exists
            if item.productvariant.product.offer:
                discount = float(item.productvariant.product.offer.discount_percentage)
                offer_price = original_price - (original_price * (discount / 100))
                item.offer_price = round(offer_price, 2)
                item.total_price = item.offer_price * item.quantity
            else:
                item.offer_price = None
                item.total_price = original_price * item.quantity
            
            total_price += item.total_price
            if not item.productvariant.is_listed or not item.productvariant.product.is_active or not item.productvariant.product.is_listed or not item.productvariant.product.subcategory.is_listed or not item.productvariant.product.subcategory.category.is_listed:
                change = True
            elif item.productvariant.quantity == 0:
                change = True
            elif item.quantity > item.productvariant.quantity:
                change = True

        if request.POST:
            pass
        context.update({
            'cart_items': cart_items,
            'total_price': round(total_price, 2),
            'addresses' : addresses
        })
        
        return render(request, 'user/summary.html',context)
    else:
        return redirect('auth_app:login')
