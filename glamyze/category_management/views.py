from django.shortcuts import render,redirect
from product_app.models import *
from django.views.decorators.cache import never_cache

# Create your views here.
@never_cache
def category_view(request):
    if request.user.is_superuser:
        #adding new categories
        if request.POST:
            new_category = request.POST['new_category']
            if new_category:
                Category.objects.create(category_name=new_category)
        category_data = Category.objects.prefetch_related('subcategory_set').order_by('id')
        return render(request,'admin/category.html',{'category_data':category_data})
    elif request.user.is_authenticated:
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
                obj = SubCategory(category_id=category_id,subcategory_name=subcategory_name)
                obj.save()
        return redirect('category_management:category_view')
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
@never_cache
def categories_list_unlist(request,id):
    if request.user.is_superuser:
        print(id)
        category_obj = Category.objects.get(id=id)
        category_obj.is_listed = not category_obj.is_listed
        category_obj.save()
        return redirect('category_management:category_view')
    elif request.user.is_authenticated:
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
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    

    


