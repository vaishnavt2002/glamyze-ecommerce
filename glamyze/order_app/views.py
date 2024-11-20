from django.shortcuts import render
from address_app.models import *
from cart_app.models import *
from django.urls import reverse
from . models import *
from django.utils import timezone
from django.db.models import Count
from django.views.decorators.cache import never_cache



# Create your views here.
@never_cache
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

@never_cache
def checkout_view(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        
        addresses = Address.objects.filter(user=request.user).order_by('id')
        context={}
        user_id = request.user.id
        cart = Cart.objects.get(user_id=user_id)
        cart_items = CartItem.objects.filter(cart=cart).select_related('cart')
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
            total_price += item.total_price
        context.update({
            'cart_items': cart_items,
            'total_price': round(total_price, 2),
            'addresses' : addresses
        })
        return render(request, 'user/checkout.html', context)
    else:
        return redirect('auth_app:login')
    
@never_cache
def order_summary(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        change = False
        context={}
        user_id = request.user.id
        cart = Cart.objects.get(user_id=user_id)
        cart_items = CartItem.objects.filter(cart=cart).select_related('cart')
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
            total_price += item.total_price
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
                change = True
            elif item.productvariant.quantity == 0:
                change = True
            elif item.quantity > item.productvariant.quantity:
                change = True

        if request.POST:
            selected_address = request.POST.get('selected_address')
            payment_method = request.POST.get('payment_method')
            summary_total = request.POST.get('summary_total')
            
            if summary_total != str(total_price):
                context['offer_change'] = True
                return render(request,'user/summary.html',context)
            try:
                address = Address.objects.get(id=selected_address)
            except:
                address = None
                context['address'] = True
            if not change:
                pass
            else:
                context['change'] = True
        context.update({
            'cart_items': cart_items,
            'total_price': round(total_price, 2),
            'selected_address' : address,
            'payment_method' : payment_method
        })

        return render(request, 'user/summary.html',context)
    else:
        return redirect('auth_app:login')
    
@never_cache
def confirm_order(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        change = False
        context={}
        user_id = request.user.id
        cart = Cart.objects.get(user_id=user_id)
        cart_items = CartItem.objects.filter(cart=cart).select_related('cart')
        total_price = 0
        if cart_items:
            for item in cart_items:
                original_price = float(item.productvariant.price)
                current_date = timezone.now().date()
                product_discount = 0
                category_discount = 0
                subcategory_discount = 0

                
                if (item.productvariant.product.offer and item.productvariant.product.offer.is_active and 
                        item.productvariant.product.offer.start_date <= current_date <= item.productvariant.product.offer.end_date):
                    product_discount = item.productvariant.price * (item.productvariant.product.offer.discount_percentage / 100)

                
                if (item.productvariant.product.subcategory.category.offer and item.productvariant.product.subcategory.category.offer.is_active and 
                        item.productvariant.product.subcategory.category.offer.start_date <= current_date <= item.productvariant.product.subcategory.category.offer.end_date):
                    category_discount = item.productvariant.price * (item.productvariant.product.subcategory.category.offer.discount_percentage / 100)

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
                total_price += item.total_price
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
                    change = True
                elif item.productvariant.quantity == 0:
                    change = True
                elif item.quantity > item.productvariant.quantity:
                    change = True
        else:
            return redirect('product_app:shop')

        if change:
            context['change']=True
            context.update({
            'cart_items': cart_items,
            'total_price': round(total_price, 2),
            })
            return render(request, 'user/summary.html',context)
                
        if request.POST:
            selected_address = request.POST.get('selected_address')
            payment_method = request.POST.get('payment_method')
            summary_total = request.POST.get('summary_total')
            if summary_total != str(total_price):
                context['offer_change'] = True
                return render(request,'user/summary.html',context)

            address = Address.objects.get(id=selected_address)
            order = Order.objects.create(user=request.user,
                                         total_amount=total_price,
                                         payment_method=payment_method,
                                         payment_status='PENDING',
                                         order_status='PROCESSING',
                                         )
            OrderAddress.objects.create(order=order,
                                        address=address,
                                        name=address.name,
                                        phone=address.phone,
                                        pincode=address.pincode,
                                        locality=address.locality,
                                        address_data=address.address,
                                        city=address.city,
                                        state=address.state,
                                        landmark=address.landmark,
                                        alternate_phone=address.alternate_phone,
                                        office_home=address.office_home
                                        )
            for item in cart_items:
                    product_variant = item.productvariant
                    original_price = float(product_variant.price)
                    
                    if item.offer_price:
                        item_offer_price = item.offer_price
                        item_price = original_price
                    else:
                        item_price = original_price
                        item_offer_price =None
                    if item_offer_price:
                        total_price = round(item_offer_price*item.quantity,2)
                    else:
                        total_price = round(item_price*item.quantity,2)
                    order_item=OrderItem(
                        order=order,
                        product_variant=product_variant,
                        quantity=item.quantity,
                        price=round(item_price, 2),
                        offer_price = item_offer_price,
                        total_price=total_price,
                    )
                    if item.offer_price:
                        if item.offer_applied == 'PRODUCT':
                            order_item.offer_applied = product_variant.product.offer
                        elif item.offer_applied == 'CATEGORY':
                            order_item.offer_applied = product_variant.product.subcategory.category.offer
                        elif item.offer_applied == 'SUBCATEGORY':
                            order_item.offer_applied = product_variant.product.subcategory.offer

                    order_item.save()
                    
                    product_variant.quantity -= item.quantity
                    product_variant.save()
            cart_items.delete()
            context['success'] = True
            return render(request, 'user/summary.html',context)
        return render(request, 'user/summary.html')
    else:
        return redirect('auth_app:login')
    
@never_cache
def order_view(request):
    orders = Order.objects.filter(user=request.user).annotate(total_items=Count('orderitem')).order_by('-id')
    return render(request,'user/orders.html',{'orders':orders})

@never_cache
def order_details(request,order_id):
    order = Order.objects.get(id=order_id)
    if request.user != order.user:
        return redirect('auth_app:logout')
    address = OrderAddress.objects.filter(order_id=order_id)
    return render(request,'user/order_details.html',{'order':order,'address':address})
    