from django.shortcuts import render,redirect
from django.http import JsonResponse
from . models import *
from django.views.decorators.cache import never_cache
from datetime import datetime
import re
from decimal import Decimal

# Create your views here.

@never_cache
def offer_view(request):
    if request.user.is_superuser:
        offers = Offer.objects.all()
        return render(request, 'my_admin/offers.html',{'offers':offers})
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
@never_cache
def add_offer(request):
    if request.user.is_superuser:
        offer_choices = Offer.OFFER_TYPE_CHOICES
        if request.POST:
            errors = []
            offer_name = request.POST.get('offer_name')
            discount_percentage = request.POST.get('discount_percentage')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            description = request.POST.get('description')
            offer_type = request.POST.get('offer_type')
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
                end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            except ValueError:
                return redirect('banner_management:add_banner')
            if Offer.objects.filter(offer_name__iexact=offer_name).exists():
                errors.append("Offer with same name already exists")
            
            if start_date and start_date.date() < datetime.today().date():
                errors.append('Start date must be today or a future date.')
            if end_date and start_date and end_date < start_date:
                errors.append('End date must be greater than or equal to the start date.')
            if  not re.match(r'^[A-Za-z0-9\s]+$',offer_name):
                errors.append('Name must contain only letters,digits and spaces')
            if len(offer_name)<3:
                errors.append('Name should atleast contain 2 letters')
            if  not re.match(r'^[A-Za-z0-9\s.]+$',description):
                errors.append('Description must contain only letters and spaces')
            if len(description)<5:
                errors.append('Description should atleast contain 5 letters')
            
            if errors:
                 context ={
                      'offer_name':offer_name,
                      'start_date':start_date,
                      'end_date':end_date,
                      'description':description,
                      'discount_percentage':discount_percentage,
                      'errors':errors,
                      'offer_type':offer_type,
                      'offer_choices':offer_choices
                 }
                 return render(request,'my_admin/add_offer.html',context)
            offer = Offer(offer_name=offer_name,
                          start_date=start_date,
                          end_date=end_date,
                          description=description,
                          discount_percentage =float(discount_percentage),
                          offer_type = offer_type
                          )
            offer.save()
            return redirect('promotion_management:offer_view')

        return render(request, 'my_admin/add_offer.html',{'offer_choices':offer_choices})
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
def edit_offer(request,offer_id):
    offer = Offer.objects.get(id=offer_id)
    offer_choices = Offer.OFFER_TYPE_CHOICES
    if request.POST:
            errors = []
            offer_name = request.POST.get('offer_name')
            discount_percentage = request.POST.get('discount_percentage')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            description = request.POST.get('description')

            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
                end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            except ValueError:
                return redirect('banner_management:add_banner')
            
            if Offer.objects.filter(offer_name__iexact=offer_name).exclude(id=offer_id).exists():
                errors.append("Offer with same name already exists")
            if end_date and start_date and end_date < start_date:
                errors.append('End date must be greater than or equal to the start date.')
            if  not re.match(r'^[A-Za-z0-9\s]+$',offer_name):
                errors.append('Name must contain only letters,digits and spaces')
            if len(offer_name)<3:
                errors.append('Name should atleast contain 2 letters')
            if  not re.match(r'^[A-Za-z0-9\s.]+$',description):
                errors.append('Description must contain only letters and spaces')
            if len(description)<5:
                errors.append('Description should atleast contain 5 letters')
            if errors:
                 context ={
                      'offer_name':offer_name,
                      'start_date':start_date,
                      'end_date':end_date,
                      'description':description,
                      'errors':errors,
                      'discount_percentage':discount_percentage,
                      'offer_choices':offer_choices,
                 }
                 return render(request,'my_admin/edit_offer.html',{'offer':offer,'offer_choices':offer_choices,'errors':errors})
            offer.offer_name=offer_name
            offer.start_date=start_date
            offer.end_date=end_date
            offer.description=description
            offer.discount_percentage =discount_percentage
                      
            offer.save()
            return redirect('promotion_management:offer_view')
    return render(request,'my_admin/edit_offer.html',{'offer':offer,'offer_choices':offer_choices})
    
def delete_offer(request,offer_id):
    if request.user.is_superuser:
        Offer.objects.get(id=offer_id).delete()
        return redirect('promotion_management:offer_view')

    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')




def activate_offer(request, offer_id):
    if request.user.is_superuser:
        if request.method == "POST":
            offer = Offer.objects.get(id=offer_id)
            offer.is_active = not offer.is_active
            offer.save()
            return JsonResponse({'status': 'success', 'is_active': offer.is_active})
        elif request.user.is_authenticated:
            if request.user.is_block:
                return redirect('auth_app:logout')
            return redirect('auth_app:home')
        else:
            return redirect('auth_app:login')
    return JsonResponse({'status': 'error'}, status=400)


@never_cache
def coupon_view(request):
    if request.user.is_superuser:
        coupons = Coupon.objects.all()
        return render(request, 'my_admin/coupons.html',{'coupons':coupons})
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    

@never_cache
def add_coupon(request):
    if request.user.is_superuser:
        if request.POST:
            errors = []
            coupon_code = request.POST.get('code')
            mininum_order_amount = request.POST.get('mininum_order_amount')
            maximum_order_amount = request.POST.get('maximum_order_amount')
            discount_amount = request.POST.get('discount_amount')
            usage_limit = request.POST.get('usage_limit')
            expiry_date = request.POST.get('expiry_date')
            try:
                expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d') if expiry_date else None
            except ValueError:
                return redirect('promotion_management:add_coupon')
            
            if Coupon.objects.filter(code__iexact=coupon_code).exists():
                errors.append("Coupon with same name already exists")
            if  not re.match(r'^[A-Za-z0-9]+$',coupon_code):
                errors.append('Code must contain only letters and number only')
            if len(coupon_code)<3:
                errors.append('Coupon should atleast contain 2 letters')

            if not usage_limit.isdigit:
                errors.append('Usage limit must be a number')
            if discount_amount>=mininum_order_amount:
                errors.append('Discount amount must be less than minimum order amount')
            if Decimal(maximum_order_amount)<=Decimal(mininum_order_amount):
                errors.append('Maximum amount must be greater than or equal to minimum order amount.')
            if expiry_date.date() < datetime.today().date():
                errors.append('Expiry date must be today or a future date.')
            
            if errors:
                 context ={
                      'code':coupon_code,
                      'mininum_order_amount':mininum_order_amount,
                      'maximum_order_amount':maximum_order_amount,
                      'discount_amount':discount_amount,
                      'usage_limit':usage_limit,
                      'errors':errors,
                      'expiry_date':expiry_date,
                 }
                 return render(request,'my_admin/add_coupon.html',context)
            coupon = Coupon(code=coupon_code,
                          mininum_order_amount=mininum_order_amount,
                          maximum_order_amount=maximum_order_amount,
                          discount_amount=discount_amount,
                          usage_limit=usage_limit,
                          expiry_date =expiry_date,
                          )
            coupon.save()
            return redirect('promotion_management:coupon_view')

        return render(request, 'my_admin/add_coupon.html')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')

def edit_coupon(request,coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    if request.POST:
            errors = []
            code = request.POST.get('code')
            mininum_order_amount = request.POST.get('mininum_order_amount')
            maximum_order_amount = request.POST.get('maximum_order_amount')
            discount_amount = request.POST.get('discount_amount')
            usage_limit = request.POST.get('usage_limit')
            expiry_date = request.POST.get('expiry_date')

            try:
                expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d') if expiry_date else None
            except ValueError:
                return redirect('promotion_management:add_coupon')
            if Coupon.objects.filter(code__iexact=code).exclude(id=coupon_id).exists():
                errors.append("Offer with same name already exists")
            if  not re.match(r'^[A-Za-z0-9]+$',code):
                errors.append('Code must contain only letters and number only')
            if len(code)<3:
                errors.append('Coupon should atleast contain 2 letters')

            if not usage_limit.isdigit:
                errors.append('Usage limit must be a number')
            if discount_amount>=mininum_order_amount:
                errors.append('Discount amount must be less than minimum order amount')
            if expiry_date.date() < datetime.today().date():
                errors.append('Expiry date must be today or a future date.')
            if Decimal(maximum_order_amount)<=Decimal(mininum_order_amount):
                errors.append('Maximum amount must be greater than or equal to minimum order amount.')
            
            if errors:
                 return render(request,'my_admin/edit_coupon.html',{'coupon':coupon,'errors':errors})
            coupon.code=code
            coupon.mininum_order_amount=mininum_order_amount
            coupon.maximum_order_amount=maximum_order_amount
            coupon.discount_amount=discount_amount
            coupon.usage_limit=usage_limit
            coupon.expiry_date =expiry_date
            coupon.save()
            return redirect('promotion_management:coupon_view')
    return render(request,'my_admin/edit_coupon.html',{'coupon':coupon})
