from django.shortcuts import render,redirect,get_object_or_404
from product_app.models import *
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import F
from django.core.paginator import Paginator

# Create your views here.
def customer_details(request):
    if request.user.is_superuser:
        if request.method == "GET":
            search = request.GET.get('searchvalue', '')
            if search:
                customer_data = CustomUser.objects.filter(
                    Q(first_name__icontains=search) | Q(email__icontains=search)
                ).exclude(is_superuser=1)
            else:
                customer_data = CustomUser.objects.exclude(is_superuser=1)
            # Pagination
            paginator = Paginator(customer_data, 10)  # Show 10 customers per page
            page_number = request.GET.get('page', 1)  # Get the page number from the request, default to 1
            page_obj = paginator.get_page(page_number)  # Get the specific page

        return render(request, 'admin/customer.html', {'customer_data': page_obj, 'searchvalue': search})
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')

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
            paginator = Paginator(products, 6)  # Show 10 customers per page
            page_number = request.GET.get('page', 1)  # Get the page number from the request, default to 1
            page_obj = paginator.get_page(page_number)  # Get the specific page

            context = {'products':page_obj,
                       'not_active':not_active,
                       'searchvalue':search, 
                       'categories':categories,
                       }
            if category_id:
                context['category_id'] = category_id
            elif subcategory_id:
                context['subcategory_id'] = subcategory_id
        return render(request,'admin/product.html',context)
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')

def product_add(request):
    if request.user.is_superuser:
        if request.POST:
            product_name = request.POST['product_name']
            price = request.POST['price']
            subcategory_id = request.POST['subcategory']
            material = request.POST['material']
            color = request.POST['color']
            description = request.POST['description']
            image1 = request.FILES['image1']
            image2 = request.FILES['image2']
            image3 = request.FILES['image3']
            product_obj=Product(product_name=product_name,price=price,subcategory_id=subcategory_id,material=material,color=color,description=description,image1=image1,image2=image2,image3=image3)
            product_obj.save()
            product_obj.refresh_from_db()
            request.session['product_id']=product_obj.id
            return redirect('product_management:product_size')
        subcategories = SubCategory.objects.select_related('category')
        context={'subcategories':subcategories}
        return render(request,'admin/addproduct.html',context)
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
def product_size(request):
    if request.user.is_superuser:
        product_id = request.session.get('product_id')
        obj = ProductSize.objects.filter(product_id=product_id)
        excluded_sizes = obj.values_list('size_id', flat=True)
        available_sizes = Size.objects.exclude(id__in=excluded_sizes)
        if request.POST:
            updated =False

            # Loop through the request.POST data to find all quantity fields
            for key, value in request.POST.items():
                if key.isdigit() and value:  # Only add to quantities if there is a value
                    size_id = int(key)  # Convert size ID from string to integer
                    try:
                        quantity = int(value) if value.strip() else 0
                    except ValueError:
                        quantity = 0  # Convert quantity from string to integer
                    product_size_obj = ProductSize.objects.get(product_id=product_id,size_id=size_id)
                    product_size_obj.quantity = quantity
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
        return render(request,'admin/productsize.html',{'product_varients':obj,'sizes':available_sizes})
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')

def size_add(request):
    if request.user.is_superuser:
        if request.POST:
            sizeid = request.POST['sizeid']
            product_id = request.session['product_id']
            obj = ProductSize(size_id=sizeid,product_id=product_id)
            obj.save()
        return redirect('product_management:product_size')
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
def list_unlist_product(request, product_id):
    if request.user.is_superuser:
        if request.method == "POST":
            product_add = Product.objects.get(id=product_id)
            product_add.is_listed = not product_add.is_listed  # Toggle the active status
            product_add.save()
            return JsonResponse({'status': 'success', 'is_listed': product_add.is_listed})
        elif request.user.is_authenticated:
            return redirect('auth_app:home')
        else:
            return redirect('auth_app:login')
    return JsonResponse({'status': 'error'}, status=400)

def inactive_product(request,product_id):
    if request.user.is_superuser:
        request.session['product_id']=product_id
        return redirect('product_management:product_size')
    elif request.user.is_authenticated:
            return redirect('auth_app:home')
    else:
            return redirect('auth_app:login')
    
    
def product_edit(request,product_id):
    if request.user.is_superuser:    
        product = Product.objects.get(id=product_id)
        subcategories = SubCategory.objects.select_related('category')
        if request.POST:
            product.product_name = request.POST.get('product_name')
            product.price = request.POST.get('price')
            product.subcategory_id = request.POST.get('subcategory')
            product.material = request.POST.get('material')
            product.color = request.POST.get('color')
            product.description = request.POST.get('description')
            if request.FILES.get('image1'):
                if product.image1:
                    product.image1.delete()
                product.image1 = request.FILES['image1']
                
            if request.FILES.get('image2'):
                if product.image2:
                    product.image2.delete()
                product.image2 = request.FILES['image2']
                
            if request.FILES.get('image3'):
                if product.image3:
                    product.image3.delete()
                product.image3 = request.FILES['image3']
            product.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_management:product_details')
        context = {
            'product': product,
            'subcategories' : subcategories

        }
        return render(request, 'admin/editproducts.html', context)
    elif request.user.is_authenticated:
            return redirect('auth_app:home')
    else:
            return redirect('auth_app:login')
    
def product_new_size(request,product_id):
    if request.user.is_superuser:
        obj = ProductSize.objects.filter(product_id=product_id)
        if request.POST:
            # Loop through the request.POST data to find all quantity fields
            for key, value in request.POST.items():
                if key.isdigit() and value:  # Only add to quantities if there is a value
                    size_id = int(key)  # Convert size ID from string to integer
                    obj = ProductSize(product_id=product_id,size_id=size_id)
                    obj.save()
            return redirect('product_management:product_details')
        excluded_sizes = obj.values_list('size_id', flat=True)
        added_size = Size.objects.filter(id__in=excluded_sizes)
        available_sizes = Size.objects.exclude(id__in=excluded_sizes)
        return render(request,'admin/newsize.html',{'added_sizes':added_size,'sizes':available_sizes})
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
def product_add_quantity(request, product_id):
    if request.user.is_superuser:
        product = get_object_or_404(Product, id=product_id)
        product_sizes = ProductSize.objects.filter(product_id=product_id)

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

        return render(request, 'admin/addquantity.html', {'product_sizes': product_sizes, 'product': product})
    
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    


