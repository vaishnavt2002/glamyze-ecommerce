from django.shortcuts import render,redirect
from product_app.models import *
from django.views.decorators.cache import never_cache
from django.db.models import Prefetch
from promotion_management.models import *
from datetime import datetime
from django.utils import timezone


# Create your views here.
@never_cache
def category_view(request):
    if request.user.is_superuser:
        if request.POST:
            new_category = request.POST['new_category']
            if new_category:
                if Category.objects.filter(category_name__iexact = new_category):
                    return render(request,'my_admin/alert.html',{'category':True})
                Category.objects.create(category_name=new_category)
        subcategory_queryset = SubCategory.objects.order_by('id')
        category_data = Category.objects.prefetch_related(Prefetch('subcategory_set', queryset=subcategory_queryset)).order_by('id')
        category_data = list(category_data)
        current_date = timezone.now().date()
        for category in category_data:
            if category.offer and category.offer.end_date >= current_date:
                category.offer_valid=True
            for subcategory in category.subcategory_set.all():
                if subcategory.offer and subcategory.offer.end_date >= current_date:
                    subcategory.offer_valid=True
        category_offers = Offer.objects.filter(is_active=True,end_date__gte = current_date,offer_type='CATEGORY')
        subcategory_offers = Offer.objects.filter(is_active=True,end_date__gte = current_date,offer_type='SUBCATEGORY')
        return render(request,'my_admin/category.html',{'category_data':category_data,'category_offers':category_offers,'subcategory_offers':subcategory_offers})
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')

@never_cache
def category_update(request):
    if request.user.is_superuser:
        if request.POST:
            category_id=request.POST['categoryid']
            new_catagory = request.POST['new_catagory_name']
            category_obj = Category.objects.get(id=category_id)
            category_obj.category_name = new_catagory
            category_obj.save()
        return redirect('category_management:category_view')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
@never_cache
def subcategory_add(request):
    if request.user.is_superuser:
        if request.POST:
            category_id = request.POST['categoryid']
            subcategory_name = request.POST.get('subcategory_name')
            if subcategory_name:
                if SubCategory.objects.filter(subcategory_name__iexact=subcategory_name,category_id=category_id):
                    return render(request,'my_admin/alert.html',{'subcategory':True})
                obj = SubCategory(category_id=category_id,subcategory_name=subcategory_name)
                obj.save()
        return redirect('category_management:category_view')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
@never_cache
def categories_list_unlist(request,id):
    if request.user.is_superuser:
        category_obj = Category.objects.get(id=id)
        category_obj.is_listed = not category_obj.is_listed
        category_obj.save()
        return redirect('category_management:category_view')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')

@never_cache
def subcategory_update(request):
    if request.user.is_superuser:
        if request.POST:
            subcategory_id=request.POST['subcategoryid']
            new_subcatagory = request.POST['new_subcatagory_name']
            subcategory_obj = SubCategory.objects.get(id=subcategory_id)
            subcategory_obj.subcategory_name = new_subcatagory
            subcategory_obj.save()
        return redirect('category_management:category_view')
    
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')

@never_cache
def subcategories_list_unlist(request,id):
    if request.user.is_superuser:
        subcategory_obj = SubCategory.objects.get(id=id)
        subcategory_obj.is_listed = not subcategory_obj.is_listed
        subcategory_obj.save()
        return redirect('category_management:category_view')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
@never_cache
def category_offer_update(request):
    if request.user.is_superuser:
        if request.POST:
            category_id = request.POST.get('category_id')
            offer_id = request.POST.get('offer_id')
            Category.objects.filter(id=category_id).update(offer_id=offer_id)
        return redirect('category_management:category_view')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
@never_cache
def subcategory_offer_update(request):
    if request.user.is_superuser:
        if request.POST:
            subcategory_id = request.POST.get('subcategory_id')
            offer_id = request.POST.get('offer_id')
            SubCategory.objects.filter(id=subcategory_id).update(offer_id=offer_id)
        return redirect('category_management:category_view')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
@never_cache
def category_offer_delete(request,category_id):
    if request.user.is_superuser:
        category = Category.objects.get(id=category_id)
        category.offer_id = None
        category.save()
        return redirect('category_management:category_view')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
@never_cache
def subcategory_offer_delete(request,subcategory_id):
    if request.user.is_superuser:
        subcategory = SubCategory.objects.get(id=subcategory_id)
        subcategory.offer_id = None
        subcategory.save()
        return redirect('category_management:category_view')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
