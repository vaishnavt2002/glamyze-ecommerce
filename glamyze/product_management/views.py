from django.shortcuts import render,redirect,get_object_or_404
from product_app.models import *
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import F
from django.core.paginator import Paginator
from PIL import Image
from django.views.decorators.cache import never_cache
from promotion_management.models import *
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from datetime import timedelta



@never_cache
def product_details(request):
    
    if request.user.is_superuser:
        if request.method == "GET":
            search = request.GET.get('searchvalue', '')
            category_id = request.GET.get('categoryid')
            subcategory_id = request.GET.get('subcategoryid')
            products = Product.objects.exclude(is_active=False).order_by('id')
            if search:
                products = products.filter(product_name__icontains=search).exclude(is_active=False)
            if category_id:
                products = products.filter(subcategory__category__id=category_id)
            elif subcategory_id:
                products = products.filter(subcategory_id=subcategory_id)
            not_active = Product.objects.filter(is_active=False)
            categories= Category.objects.prefetch_related('subcategory_set')
            paginator = Paginator(products, 6)
            page_number = request.GET.get('page', 1) 
            page_obj = paginator.get_page(page_number)  

            context = {'products':page_obj,
                       'not_active':not_active,
                       'searchvalue':search, 
                       'categories':categories,
                       }
            if category_id:
                context['category_id'] = category_id
            elif subcategory_id:
                context['subcategory_id'] = subcategory_id
        return render(request,'my_admin/product.html',context)
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')

@never_cache
def product_add(request):
    if request.user.is_superuser:
        subcategories = SubCategory.objects.select_related('category')
        current_date = timezone.now().date()
        offers = Offer.objects.filter(is_active=True,end_date__gte = current_date)
        context={'subcategories':subcategories,'offers':offers}
        if request.POST:
            product_name = request.POST['product_name']
            subcategory_id = request.POST['subcategory']
            material = request.POST['material']
            color = request.POST['color']
            description = request.POST['description']
            image1 = request.FILES['image1']
            image2 = request.FILES['image2']
            image3 = request.FILES['image3']
            errors = []
            error1 = validate_image_format(image1,'Image1')
            error2 = validate_image_format(image2,'Image2')
            error3 = validate_image_format(image3,'Image3')
            if error1:
                errors.append(error1)
            if error2:
                errors.append(error2)
            if error3:
                errors.append(error3)
            if errors:
                context.update({'product_name':product_name,'subcategory_id':subcategory_id,'material':material,'color':color,'description':description,'errors':errors})
                return render(request,'admin/addproduct.html',context)

            product_obj=Product(product_name=product_name,subcategory_id=subcategory_id,material=material,color=color,description=description,image1=image1,image2=image2,image3=image3)
            offer_id = request.POST.get('offer_id')
            if offer_id:
                product_obj.offer_id = offer_id
            product_obj.save()
            product_obj.refresh_from_db()
            request.session['product_id']=product_obj.id
            return redirect('product_management:product_size')
        return render(request,'my_admin/addproduct.html',context)
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    

def validate_image_format(image,image_name):
            try:
                with Image.open(image) as img:
                    if img.format.lower() not in ['png', 'jpg', 'jpeg']:
                        return f"{image_name} must be a PNG or JPG file."
                    else:
                        return None
            except Exception:
                    return f"{image_name} is not a valid image file."


@never_cache
def product_size(request):
    if request.user.is_superuser:
        product_id = request.session.get('product_id')
        obj = ProductVariant.objects.filter(product_id=product_id)
        excluded_sizes = obj.values_list('size_id', flat=True)
        available_sizes = Size.objects.exclude(id__in=excluded_sizes)
        if request.POST:
            updated =False

            for key, value in request.POST.items():
                if key.isdigit() and value:
                    size_id = int(key)
                    try:
                        quantity = int(value) if value.strip() else 0
                    except ValueError:
                        quantity = 0 
                    product_size_obj = ProductVariant.objects.get(product_id=product_id,size_id=size_id)
                    product_size_obj.quantity = quantity
                    price_key = f'price{size_id}'
                    price = request.POST.get(price_key, '0')
                    price = float(price) if price.strip() else 0.0
                    product_size_obj.price = price
                    product_size_obj.is_listed = True
                    product_size_obj.save()
                    updated = True
            if updated:
                is_listed = request.POST.get('is_list')
                product_obj = Product.objects.get(id=product_id)
                product_obj.is_active = True
                product_obj.is_listed = True if is_listed == 'on' else False
                product_obj.save()
            del request.session['product_id']
            return redirect('product_management:product_details')
        return render(request,'my_admin/productsize.html',{'product_varients':obj,'sizes':available_sizes})
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
@never_cache
def size_add(request):
    if request.user.is_block:
        return redirect('auth_app:logout')
    if request.user.is_superuser:
        if request.POST:
            sizeid = request.POST['sizeid']
            product_id = request.session['product_id']
            obj = ProductVariant(size_id=sizeid,product_id=product_id,is_listed=False)
            obj.save()
        return redirect('product_management:product_size')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')

@never_cache
def list_unlist_product(request, product_id):
    if request.user.is_block:
        return redirect('auth_app:logout')
    if request.user.is_superuser:
        if request.method == "POST":
            product_add = Product.objects.get(id=product_id)
            product_add.is_listed = not product_add.is_listed
            product_add.save()
            return JsonResponse({'status': 'success', 'is_listed': product_add.is_listed})
        elif request.user.is_authenticated:
            if request.user.is_block:
                return redirect('auth_app:logout') 
            return redirect('auth_app:home')
        else:
            return redirect('auth_app:login')
    return JsonResponse({'status': 'error'}, status=400)

@never_cache
def inactive_product(request,product_id):
    if request.user.is_block:
        return redirect('auth_app:logout')
    if request.user.is_superuser:
        request.session['product_id']=product_id
        return redirect('product_management:product_size')
    elif request.user.is_authenticated:
            if request.user.is_block:
                return redirect('auth_app:logout') 
            return redirect('auth_app:home')
    else:
            return redirect('auth_app:login')
    

@never_cache  
def product_edit(request,product_id):
    if request.user.is_block:
        return redirect('auth_app:logout')
    if request.user.is_superuser:    
        product = Product.objects.get(id=product_id)
        current_date = timezone.now().date()
        offers = Offer.objects.filter(is_active=True,end_date__gte = current_date)
        subcategories = SubCategory.objects.select_related('category')
        context = {
            'product': product,
            'subcategories' : subcategories,
            'offers':offers

        }
        if request.POST:
            errors = []
            if request.FILES.get('image1'):
                image1 = request.FILES.get('image1')
                error1 = validate_image_format(image1,'Image1')
                if error1:
                    errors.append(error1)
                    
                else:
                    if product.image1:
                        product.image1.delete()
                    product.image1 = request.FILES['image1']
                
            if request.FILES.get('image2'):
                image2 = request.FILES.get('image2')
                error2 = validate_image_format(image2,'Image2')
                if error2:
                    errors.append(error2)
                else:
                    if product.image2:
                        product.image2.delete()
                    product.image2 = request.FILES['image2']
                
            if request.FILES.get('image3'):
                image3 = request.FILES.get('image3')
                error3 = validate_image_format(image3,'Image3')
                if error3:
                    errors.append(error3)
                else:
                    if product.image3:
                        product.image3.delete()
                    product.image3 = request.FILES['image3']
            if errors:
                print(errors)
                context['errors'] = errors
                return render(request, 'my_admin/editproducts.html',context)
            offer_id = request.POST.get('offer_id')
            if offer_id=='null':
                product.offer_id = None
            else:
                product.offer_id = offer_id
            product.product_name = request.POST.get('product_name')
            product.subcategory_id = request.POST.get('subcategory')
            product.material = request.POST.get('material')
            product.color = request.POST.get('color')
            product.description = request.POST.get('description')
            product.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_management:product_details')
       
        return render(request, 'my_admin/editproducts.html', context)
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    else:
            return redirect('auth_app:login')


@never_cache
def product_varient_management(request,product_id):
    if request.user.is_block:
        return redirect('auth_app:logout')
    if request.user.is_superuser:
        
        if request.POST:
            for key, value in request.POST.items():
                if key.isdigit() and value:
                    size_id = int(key) 
                    if ProductVariant.objects.filter(product_id=product_id,size_id=size_id):
                        pass
                    else:
                        obj = ProductVariant(product_id=product_id,size_id=size_id,is_listed=False)
                        obj.save()
        obj = ProductVariant.objects.filter(product_id=product_id)
        excluded_sizes = obj.values_list('size_id', flat=True)
        product = Product.objects.get(id=product_id)
        # Get added sizes with their listing status
        added_sizes_with_status = []
        for variant in obj:
            added_sizes_with_status.append({
                'size': variant.size,
                'is_listed': variant.is_listed,
                'price' : variant.price
            })
        
        available_sizes = Size.objects.exclude(id__in=excluded_sizes)
        return render(request,'my_admin/varient_mgmt.html',{'product':product, 'added_sizes':added_sizes_with_status,'sizes':available_sizes})
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
def product_varient_management_post(request):
    if request.user.is_block:
        return redirect('auth_app:logout')
    if request.user.is_superuser:
        if request.POST:
            product_id = request.POST['product_id']
            variants = ProductVariant.objects.filter(product_id=product_id)
            for variant in variants:
                if request.POST.get(f'listed{variant.size.id}'):
                    variant.is_listed = True
                else:
                    variant.is_listed = False
                variant.price= request.POST.get(f'price{variant.size.id}')
                variant.save()
            return redirect('product_management:product_details')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')



@never_cache
def product_add_quantity(request, product_id):
    if request.user.is_block:
        return redirect('auth_app:logout')
    if request.user.is_superuser:
        product = Product.objects.get(id=product_id)
        product_sizes = ProductVariant.objects.filter(product_id=product_id)

        if request.method == 'POST':
            updated_count = 0
            for product_size in product_sizes:
                product_size_id = str(product_size.id)
                if product_size_id in request.POST:
                    quantity_to_add = request.POST.get(product_size_id,0)
                    if quantity_to_add:
                        quantity_to_add = int(quantity_to_add)
                    else:
                        quantity_to_add = 0
                    if quantity_to_add > 0:
                        product_size.quantity = F('quantity') + quantity_to_add
                        product_size.save()
                        updated_count += 1
            if updated_count > 0:
                messages.success(request, f'{updated_count} size(s) updated successfully!')
            return redirect('product_management:product_details')

        return render(request, 'my_admin/addquantity.html', {'product_sizes': product_sizes, 'product': product})
    
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
