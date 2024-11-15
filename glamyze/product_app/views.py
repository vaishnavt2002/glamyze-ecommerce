from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.cache import never_cache
from product_app.models import *
from django.core.paginator import Paginator
from django.db.models import Prefetch,Count
from django.db.models import Q,Sum,Min
from datetime import datetime
from django.utils import timezone



@never_cache
def shop(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        search = request.GET.get('searchvalue', '')
        category_id = request.GET.get('category_id')
        subcategory_id = request.GET.get('subcategory_id')
        sort = request.GET.get('sort')
        price_range =request.GET.get('price_range')
        categories = Category.objects.exclude(is_listed=False)
        categories = categories.prefetch_related(Prefetch('subcategory_set',queryset=SubCategory.objects.filter(is_listed=True)))
        products = Product.objects.filter(
            is_active=True,
            is_listed=True,
            subcategory__category__is_listed=True,
            subcategory__is_listed=True,
            productvariant__is_listed=True
        ).annotate(total_stock=Sum('productvariant__quantity')).distinct().order_by('id')
        if search:
            products = products.filter(product_name__icontains=search).exclude(is_active=False)
        if category_id:
            products = products.filter(subcategory__category__id=category_id)
        elif subcategory_id:
            products = products.filter(subcategory_id=subcategory_id)
        
        products = products.prefetch_related(Prefetch('productvariant_set',queryset=ProductVariant.objects.filter(is_listed=True).order_by('price')))
        products = products.annotate(lowest_price = Min('productvariant__price'))
        if sort:
            if sort == 'id':
                products.order_by('id')
            elif sort == 'newness':
                products.order_by('-id')
            elif sort == 'rating':
                pass
            elif sort == 'popularity':
                products = products.annotate(popularity=Count('productvariant__orderitem')).order_by('-popularity')
            elif sort =='low':
                products = products.order_by('lowest_price')
            elif sort == 'high':
                products = products.order_by('-lowest_price')
            elif sort == 'az':
                products = products.order_by('product_name')
            elif sort == 'za':
                products = products.order_by('-product_name')
        if price_range:
            if price_range != 'all':
                min,max = price_range.split('-')
                if max == "":
                   products = products.filter(lowest_price__gte=min)
                else:
                   products = products.filter(lowest_price__gte=min,lowest_price__lte=max)

                
                
        paginator = Paginator(products, 4)
        page_number = request.GET.get('page', 1) 
        page_obj = paginator.get_page(page_number) 
        
        for product in page_obj:
            variant = product.productvariant_set.first() if product.productvariant_set.exists() else None
            if variant:
                product.variant_price = variant.price
                product.price = variant.price
                # Calculate offer price if product has an active offer
                current_date = timezone.now().date()
                if (product.offer and product.offer.is_active and 
                            product.offer.start_date <= current_date <= product.offer.end_date):
                    discount = product.offer.discount_percentage
                    product.offer_price = round(variant.price * (1 - discount / 100), 2)
                    product.price = product.offer_price
                else:
                    product.offer_price = None
    

        context = {
            'products': page_obj,
            'searchvalue': search,
            'page_obj': page_obj,
            'categories': categories,
            'sort':sort,
            'price_range':price_range

        }
        if sort:
            context['sort'] = sort
        if category_id:
            context['category_id'] = category_id
        elif subcategory_id:
            context['subcategory_id'] = subcategory_id

        return render(request, 'user/shop.html', context)
    else:
        return redirect('auth_app:login')

    

    
@never_cache
def product_view(request, product_id):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')  
        
        product = get_object_or_404(Product, id=product_id)

        if not product.is_active or not product.is_listed:
            return redirect('product_app:shop')

        if not product.subcategory.is_listed or not product.subcategory.category.is_listed:
            return redirect('product_app:shop')

        sizes = ProductVariant.objects.filter(product_id=product_id, is_listed=True).order_by('price')
        if not sizes.exists():
            return redirect('product_app:shop')

        selected_size = sizes.first()

        if request.GET:
            size = request.GET.get('size')
            try:
                selected_size = sizes.get(size_id=size)
            except ProductVariant.DoesNotExist:
                return redirect('product_app:shop')
        
        # Check if product has an active offer within valid dates
        current_date = timezone.now().date()
        if (product.offer and product.offer.is_active and 
            product.offer.start_date <= current_date <= product.offer.end_date):
            # Calculate offer price for selected size
            discount = product.offer.discount_percentage
            selected_size.offer_price = round(selected_size.price * (1 - discount / 100), 2)
            selected_size.has_offer = True
        else:
            selected_size.offer_price = None
            selected_size.has_offer = False

        related_products = Product.objects.filter(
            is_active=True,
            is_listed=True,
            subcategory__category__is_listed=True,
            subcategory__is_listed=True,
            productvariant__is_listed=True,
            subcategory_id=product.subcategory.id
        ).distinct().exclude(id=product_id).order_by('id')[0:8]
        
        related_products = related_products.prefetch_related(
            Prefetch('productvariant_set', 
                    queryset=ProductVariant.objects.filter(is_listed=True)))
        
        # Calculate offer prices for related products
        for item in related_products:
            variant = item.productvariant_set.first() if item.productvariant_set.exists() else None
            if variant:
                item.variant_price = variant.price
                if (item.offer and item.offer.is_active and 
                    item.offer.start_date <= current_date <= item.offer.end_date):
                    item.offer_price = round(variant.price * (1 - item.offer.discount_percentage / 100), 2)
                    item.has_offer = True
                else:
                    item.offer_price = None
                    item.has_offer = False

        return render(request, 'user/product_view.html', {
            'product': product,
            'sizes': sizes,
            'selected_size': selected_size,
            'related_products': related_products,
        })
    else:
        return redirect('auth_app:login')

