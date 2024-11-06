from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.cache import never_cache
from product_app.models import *
from django.core.paginator import Paginator
from django.db.models import Prefetch,Count
from django.db.models import Q


@never_cache
def shop(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')
    elif request.user.is_block:
        return redirect('auth_app:logout')  
    if request.user.is_authenticated:
        search = request.GET.get('searchvalue', '')
        category_id = request.GET.get('categoryid')
        subcategory_id = request.GET.get('subcategoryid')
        categories = Category.objects.exclude(is_listed=False)
        categories = categories.prefetch_related(Prefetch('subcategory_set',queryset=SubCategory.objects.filter(is_listed=True)))
        products = Product.objects.filter(
            is_active=True,
            is_listed=True,
            subcategory__category__is_listed=True,
            subcategory__is_listed=True,
            productvariant__is_listed=True
        ).distinct().order_by('id')
        if search:
            products = products.filter(product_name__icontains=search).exclude(is_active=False)
        if category_id:
            products = products.filter(subcategory__category__id=category_id)
        elif subcategory_id:
            products = products.filter(subcategory_id=subcategory_id)
        
        

        products = products.prefetch_related(Prefetch('productvariant_set',queryset=ProductVariant.objects.filter(is_listed=True)))
        paginator = Paginator(products, 4)
        page_number = request.GET.get('page', 1) 
        page_obj = paginator.get_page(page_number) 
        
        for product in page_obj:
            variant_price = product.productvariant_set.first().price if product.productvariant_set.exists() else None
            product.variant_price = variant_price

        context = {
            'products': page_obj,
            'searchvalue': search,
            'page_obj': page_obj,
            'categories': categories,
        }
        if category_id:
            context['category_id'] = category_id
        elif subcategory_id:
            context['subcategory_id'] = subcategory_id

        return render(request, 'user/shop.html', context)
    else:
        return redirect('auth_app:login')

    

    
@never_cache
def product_view(request, product_id):
    # Check if user is a superuser and redirect to admin dashboard
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    elif request.user.is_block:
        return redirect('auth_app:logout') 

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Get the product or return a 404 if not found
        product = get_object_or_404(Product, id=product_id)

        # Check if the product is active and listed
        if not product.is_active or not product.is_listed:
            return redirect('product_app:shop')  # Redirect to the shop page

        # Check if the associated category and subcategory are active and listed
        if not product.subcategory.is_listed or not product.subcategory.category.is_listed:
            return redirect('product_app:shop')  # Redirect if category or subcategory is unlisted

        # Fetch available sizes for the product
        sizes = ProductVariant.objects.filter(product_id=product_id, is_listed=True)  # Only listed variants
        if not sizes.exists():
            return redirect('product_app:shop')  # Redirect if no sizes available

        # Default to the first available size
        selected_size = sizes.first()

        # If a size is selected via GET request, update the selected size
        if request.GET:
            size = request.GET.get('size')
            try:
                selected_size = sizes.get(size_id=size)
            except ProductVariant.DoesNotExist:
                return redirect('product_app:shop')  # Redirect if size does not exist
        

        #related products creation
        related_products = Product.objects.filter(
            is_active=True,
            is_listed=True,
            subcategory__category__is_listed=True,
            subcategory__is_listed=True,
            productvariant__is_listed=True,
            subcategory_id = product.subcategory.id
        ).distinct().exclude(id=product_id).order_by('id')[0:8]
        related_products = related_products.prefetch_related(Prefetch('productvariant_set',queryset=ProductVariant.objects.filter(is_listed=True)))
        for item in related_products:
            variant_price = item.productvariant_set.first().price if item.productvariant_set.exists() else None
            item.variant_price = variant_price

        return render(request, 'user/product_view.html', {
            'product': product,
            'sizes': sizes,
            'selected_size': selected_size,
            'related_products': related_products
        })
    
    else:
        return redirect('auth_app:login')
    

