from django.shortcuts import render,HttpResponse,redirect
from address_app.models import *
from cart_app.models import *
from django.urls import reverse
from . models import *
from django.utils import timezone
from django.db.models import Count
from django.views.decorators.cache import never_cache
import razorpay
from django.conf import settings
from wallet_app.models import *
from decimal import Decimal



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
            total_price += float(item.total_price)
            
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
            total_price += float(item.total_price)
        #coupon checking
        coupon_applied = False
        if request.session.get('coupon_code'):
            code = request.session.get('coupon_code')
            if Coupon.objects.filter(code=code).exists():
                coupon = Coupon.objects.get(code=code)
                if current_date<= coupon.expiry_date and coupon.mininum_order_amount <= total_price<= coupon.maximum_order_amount:
                    usage_count = Order.objects.filter(user=request.user,coupon=coupon).count()
                    if usage_count < coupon.usage_limit:
                        coupon_applied = coupon
                        total_price -= float(coupon.discount_amount)
                        
                    else:
                        context['coupon_failed']='Coupon Limit Reached'
                        del request.session['coupon_code']
                else:
                    context['coupon_failed']='Invalid Coupon'
                    del request.session['coupon_code']
        #check the wallet amount to know is it possible to use wallet.
        wallet_obj,created = Wallet.objects.get_or_create(user=request.user)
        wallet_enabled = False
        if wallet_obj.balance:
            if wallet_obj.balance >= total_price:
                wallet_enabled = True
        context.update({
            'cart_items': cart_items,
            'total_price': round(total_price, 2),
            'addresses' : addresses,
            'coupon_applied' : coupon_applied,
            'wallet_enabled' : wallet_enabled
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
                change = True
            elif item.productvariant.quantity == 0:
                change = True
            elif item.quantity > item.productvariant.quantity:
                change = True
        coupon_applied = False
        if request.session.get('coupon_code'):
            code = request.session.get('coupon_code')
            if Coupon.objects.filter(code=code).exists():
                coupon = Coupon.objects.get(code=code)
                if current_date<= coupon.expiry_date and coupon.mininum_order_amount <= total_price<= coupon.maximum_order_amount:
                    usage_count = Order.objects.filter(user=request.user,coupon=coupon).exclude(order_status='PENDING').count()
                    if usage_count < coupon.usage_limit:
                        coupon_applied = coupon
                        total_price -= float(coupon.discount_amount)

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
            'payment_method' : payment_method,
            'coupon_applied' : coupon_applied
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
        coupon_applied = None
        if request.session.get('coupon_code'):
            code = request.session.get('coupon_code')
            if Coupon.objects.filter(code=code).exists():
                coupon = Coupon.objects.get(code=code)
                if current_date<= coupon.expiry_date and coupon.mininum_order_amount <= total_price<= coupon.maximum_order_amount:
                    usage_count = Order.objects.filter(user=request.user,coupon=coupon).count()
                    if usage_count < coupon.usage_limit:
                        coupon_applied = coupon
                        total_price -= float(coupon.discount_amount)
                        del request.session['coupon_code']
        
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
                                            order_status='PENDING',
                                            coupon=coupon_applied
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
                    
            if payment_method == 'cod':
                order_items = OrderItem.objects.filter(order=order)
                for item in order_items:
                    product_variant = item.product_variant
                    product_variant.quantity = product_variant.quantity - item.quantity
                    product_variant.save()
                order.order_status='PROCESSING'
                order.save()
                cart_items.delete()
                context['success'] = True
            if payment_method == 'wallet':
                order_items = OrderItem.objects.filter(order=order)
                for item in order_items:
                    product_variant = item.product_variant
                    product_variant.quantity = product_variant.quantity - item.quantity
                    product_variant.save()
                order.order_status='PROCESSING'
                order.payment_status = 'PAID'
                order.payment_method = 'wallet'
                wallet,created = Wallet.objects.get_or_create(user=request.user)
                if wallet.balance >= order.total_amount:
                    transaction = WalletTransaction(wallet=wallet, transaction_type='DEBIT',amount=order.total_amount)
                    wallet.balance -= Decimal(order.total_amount)
                    transaction.save()
                    wallet.save()
                    order.save()
                    cart_items.delete()
                    context['success'] = True
                else:
                    context['failed'] = True
            if payment_method == 'razorpay':
                client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID,settings.KEY_SECRET))
                payment = client.order.create({'amount' : int(float(summary_total)*100), 'currency':'INR','payment_capture':1})
                print(payment)
                context = {'payment':payment,'key':settings.RAZOR_PAY_KEY_ID}
                order.razorpay_order_id=payment['id']
                order.save()
                return render(request,'user/payment.html',context)
            return render(request, 'user/summary.html',context)
        
        return render(request, 'user/summary.html')
    else:
        return redirect('auth_app:login')
    
@never_cache
def order_view(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        orders = Order.objects.filter(user=request.user).exclude(order_status='PENDING').annotate(total_items=Count('orderitem')).order_by('-id')
        return render(request,'user/orders.html',{'orders':orders})
        
    else:
        return redirect('auth_app:login')
    

@never_cache
def order_details(request,order_id):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        order = Order.objects.prefetch_related('orderitem_set').get(id=order_id)

        if request.user != order.user:
            return redirect('auth_app:logout')
        return_enabled = False
        if order.order_status == 'DELIVERED':
            return_enabled = True        
        address = OrderAddress.objects.filter(order_id=order_id)
        order_items = order.orderitem_set.all()
        
        return render(request,'user/order_details.html',{'order':order,'address':address,'return_enabled':return_enabled})
        
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
            try:
                order = Order.objects.get(razorpay_order_id=order_id,payment_status='PENDING')
            except:
                return render(request,'user/alert.html',{'failed':True})
            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                if item.product_variant.quantity<item.quantity:
                    
                    if Wallet.objects.filter(user=request.user).exists():
                        wallet = Wallet.objects.get(user=request.user)
                    else:
                        wallet = Wallet.objects.create(user=request.user)
                    transacion=WalletTransaction(wallet=wallet,transaction_type='REFUND',amount=order.total_amount)
                    transacion.save()
                    wallet.balance += Decimal(order.total_amount)
                    wallet.save()
                    order.order_status = 'FAILED'
                    order.payment_status = 'REFUNDED'
                    order.save()
                    return render(request,'user/alert.html',{'quantity_failed':True})
            order.razorpay_payment_id = payment_id
            order.payment_status = 'PAID'
            order.order_status = 'PROCESSING'
            order.save()
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart).select_related('cart')
            cart_items.delete()
            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                product_variant = item.product_variant
                product_variant.quantity = product_variant.quantity - item.quantity
                product_variant.save()
        return render(request,'user/alert.html',{'success':True})
        
    else:
        return redirect('auth_app:login')
    

def payment_failure(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        order_id = request.GET.get('order_id')
        order = Order.objects.get(razorpay_order_id=order_id)
        order.payment_status = 'FAILED'
        order.order_status = 'FAILED'
        order.save()
        return render(request,'user/alert.html',{'failed':True})
        
    else:
        return redirect('auth_app:login')
    


@never_cache
def apply_coupon(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        if request.POST:
            code = request.POST.get('code')
            request.session['coupon_code'] = code
        return redirect('order_app:checkout_view')
        
    else:
        return redirect('auth_app:login')
    
def cancel_order(request,order_id):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        if request.POST:
            cancel_reason = request.POST.get('cancel_reason')
            if request.POST.get('explanation'):
                explantion = request.POST.get('explanation')
                explantion = "-"+explantion
                cancel_reason += explantion
            order = Order.objects.get(id=order_id)
            if request.user == order.user and order.order_status!='DELIVERED':
                print('HI')
                cancel=OrderCancellation(order_id=order_id, reason_type=cancel_reason, cancelled_by='CUSTOMER')
                
                order.order_status='CANCELLED'
                order.payment_status = 'REFUNDED'
                
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
                order.save()
                cancel.save()
                return redirect('order_app:order_details', order_id=order_id)
            else:
                return redirect('auth_app:logout')
        
    else:
        return redirect('auth_app:login')
    

def return_product(request):
    if request.POST:
        item_id = request.POST.get('item_id')
        return_reason = request.POST.get('return_reason')
        return_explanation = request.POST.get('return_explanation', '')
        try:
            order_item = OrderItem.objects.get(id=item_id)
        except:
            return redirect('order_app:order_view')
        if request.user == order_item.order.user:
            if order_item.order.order_status == 'DELIVERED':
                if OrderReturn.objects.filter(order_item=order_item).exists():
                    pass
                else:
                    return_obj = OrderReturn(order_item=order_item,return_reason=return_reason,return_explanation= return_explanation if return_explanation else None,status='REQUESTED')
                    return_obj.save()
                return redirect('order_app:order_details',order_id = order_item.order_id)
            else:
                return redirect('order_app:order_details',order_id = order_item.order_id)
        else:
            return redirect('auth_app:logout')
            
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Order, OrderItem, OrderAddress
import datetime


def generate_invoice_pdf(request, order_id):
   # Fetch the order and related data
   order = Order.objects.get(id=order_id)
   order_items = OrderItem.objects.filter(order=order)
   order_address = OrderAddress.objects.get(order=order)


   # Prepare data for the template
   context = {
       'order': order,
       'order_items': order_items,
       'order_address': order_address,
       'subtotal': order.get_subtotal(),
       'offer_discount': order.get_offer_discount(),
       'coupon_discount': order.get_coupon_discount(),
       'total_amount': order.total_amount,
       'date': datetime.datetime.now().strftime('%Y-%m-%d'),
   }


   # Render the HTML template
   html_string = render_to_string('invoice_print.html', context)


   # Generate the PDF
   pdf_file = HTML(string=html_string).write_pdf()


   # Return the PDF as a response
   response = HttpResponse(pdf_file, content_type='application/pdf')
   response['Content-Disposition'] = f'attachment; filename="invoice_{order_id}.pdf"'
   return response
