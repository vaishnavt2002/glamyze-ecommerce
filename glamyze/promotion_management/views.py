from django.shortcuts import render,redirect
from django.http import JsonResponse
from . models import *
from django.views.decorators.cache import never_cache
from datetime import datetime

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
            
            if start_date and start_date.date() < datetime.today().date():
                errors.append('Start date must be today or a future date.')
            if end_date and start_date and end_date < start_date:
                errors.append('End date must be greater than or equal to the start date.')
            if errors:
                 context ={
                      'offer_name':offer_name,
                      'start_date':start_date,
                      'end_date':end_date,
                      'description':description,
                      'errors':errors
                 }
                 return render(request,'my_admin/add_offer.html',context)
            offer = Offer(offer_name=offer_name,
                          start_date=start_date,
                          end_date=end_date,
                          description=description,
                          discount_percentage =float(discount_percentage)
                          )
            offer.save()
            return redirect('promotion_management:offer_view')

        return render(request, 'my_admin/add_offer.html')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
def edit_offer(request,offer_id):
    offer = Offer.objects.get(id=offer_id)
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
            
            if start_date and start_date.date() < datetime.today().date():
                errors.append('Start date must be today or a future date.')
            if end_date and start_date and end_date < start_date:
                errors.append('End date must be greater than or equal to the start date.')
            if errors:
                 context ={
                      'offer_name':offer_name,
                      'start_date':start_date,
                      'end_date':end_date,
                      'description':description,
                      'errors':errors
                 }
                 return render(request,'my_admin/add_offer.html',context)
            offer.offer_name=offer_name
            offer.start_date=start_date
            offer.end_date=end_date
            offer.description=description
            offer.discount_percentage =discount_percentage
                      
            offer.save()
            return redirect('promotion_management:offer_view')
    return render(request,'my_admin/edit_offer.html',{'offer':offer})
    
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