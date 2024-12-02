from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.cache import never_cache
from product_app.models import *
from django.core.paginator import Paginator
from django.db.models import Prefetch,Count
from django.db.models import Q,Sum,Min,Avg
from datetime import datetime
from django.utils import timezone
from cart_app.models import *
from wishlist_app.models import *
from order_app.models import *
from django.contrib import messages
from django.db.models.functions import Coalesce



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
        
        products = products.prefetch_related(Prefetch('productvariant_set',queryset=ProductVariant.objects.filter(is_listed=True).order_by('-quantity')))
        products = products.annotate(lowest_price = Min('productvariant__price'))
        
        if price_range:
            if price_range != 'all':
                min_value,max_value = price_range.split('-')
                if max_value == "":
                   products = products.filter(lowest_price__gte=min_value)
                else:
                   products = products.filter(lowest_price__gte=min_value,lowest_price__lte=max_value)

        if sort:
            if sort == 'id':
                products.order_by('id')
            elif sort == 'newness':
                print('worked')
                products = products.order_by('-id')
            elif sort == 'rating':
                products = products.annotate(avg_rating=Coalesce(Avg('productreview__rating'), 0.0)).order_by('-avg_rating')
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
                
        paginator = Paginator(products, 12)
        page_number = request.GET.get('page', 1) 
        page_obj = paginator.get_page(page_number) 
        
        for product in page_obj:
            variant = product.productvariant_set.first() if product.productvariant_set.exists() else None
            if variant:
                product.variant_price = variant.price
                product.price = variant.price
                current_date = timezone.now().date()

                # Initialize variables for different offer discounts
                product_discount = 0
                category_discount = 0
                subcategory_discount = 0

                # Check for product-level offer
                if (product.offer and product.offer.is_active and 
                        product.offer.start_date <= current_date <= product.offer.end_date):
                    product_discount = variant.price * (product.offer.discount_percentage / 100)

                # Check for category-level offer
                if (product.subcategory.category.offer and product.subcategory.category.offer.is_active and 
                        product.subcategory.category.offer.start_date <= current_date <= product.subcategory.category.offer.end_date):
                    category_discount = variant.price * (product.subcategory.category.offer.discount_percentage / 100)

                # Check for subcategory-level offer
                if (product.subcategory.offer and product.subcategory.offer.is_active and 
                        product.subcategory.offer.start_date <= current_date <= product.subcategory.offer.end_date):
                    subcategory_discount = variant.price * (product.subcategory.offer.discount_percentage / 100)

                # Determine the highest discount
                max_discount = max(product_discount, category_discount, subcategory_discount)

                # Apply the highest discount to the product price
                if max_discount > 0:
                    product.offer_price = round(variant.price - max_discount, 2)
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

        sizes = ProductVariant.objects.filter(product_id=product_id, is_listed=True).order_by('-quantity')
        if not sizes.exists():
            return redirect('product_app:shop')

        selected_size = sizes.first()
        if request.GET:
            size = request.GET.get('size')
            try:
                selected_size = sizes.get(size_id=size)
            except ProductVariant.DoesNotExist:
                return redirect('product_app:shop')
        
        current_date = timezone.now().date()
        product_discount = 0
        category_discount = 0
        subcategory_discount = 0
        # Check for product-level offer
        if (product.offer and product.offer.is_active and 
                        product.offer.start_date <= current_date <= product.offer.end_date):
                    product_discount = selected_size.price * (product.offer.discount_percentage / 100)

        # Check for category-level offer
        if (product.subcategory.category.offer and product.subcategory.category.offer.is_active and 
                        product.subcategory.category.offer.start_date <= current_date <= product.subcategory.category.offer.end_date):
                    category_discount = selected_size.price * (product.subcategory.category.offer.discount_percentage / 100)

        # Check for subcategory-level offer
        if (product.subcategory.offer and product.subcategory.offer.is_active and 
                        product.subcategory.offer.start_date <= current_date <= product.subcategory.offer.end_date):
                    subcategory_discount = selected_size.price * (product.subcategory.offer.discount_percentage / 100)

        
        max_discount = max(product_discount, category_discount, subcategory_discount)
        if max_discount > 0:
            selected_size.offer_price = round(selected_size.price - max_discount, 2)
            selected_size.has_offer = True
            if max_discount == product_discount:
                offer_applied = 'PRODUCT'
            elif max_discount == subcategory_discount:
                offer_applied = 'SUBCATEGORY'
            elif max_discount == category_discount:
                offer_applied = 'CATEGORY'
        else:
            selected_size.offer_price = None
            selected_size.has_offer = False
            offer_applied = None

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
        cart = Cart.objects.filter(user=request.user).first()
        added = False
        if cart:
            added = CartItem.objects.filter(cart=cart, productvariant=selected_size).exists()
        wishlisted = False
        if Wishlist.objects.filter(user=request.user).exists():
            wishlist = Wishlist.objects.get(user=request.user)
            if WishlistItem.objects.filter(wishlist=wishlist,productvariant=selected_size).exists():
                wishlisted = True
        if ProductReview.objects.filter(user=request.user,product=product).exists():
            review_added = True
            item_bought = True
        elif OrderItem.objects.filter(order__user=request.user,product_variant__product=product).exists():
            review_added = False
            item_bought = True
        else:
            review_added =False
            item_bought = False
        reviews = ProductReview.objects.filter(product=product).order_by('-created_at')[:5]
        avg_rating = ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('rating'))['avg_rating']
        avg_rating = round(avg_rating,1) if avg_rating else 0.0
        print(selected_size)
        return render(request, 'user/product_view.html', {
            'product': product,
            'sizes': sizes,
            'selected_size': selected_size,
            'related_products': related_products,
            'added' : added,
            'offer_applied':offer_applied,
            'wishlisted' : wishlisted,
            'review_added': review_added,
            'reviews' : reviews,
            'avg_rating' : avg_rating,
            'item_bought':item_bought
        })
    else:
        return redirect('auth_app:login')
    
def product_review(request,product_id):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        
        if request.POST:
            rating = request.POST.get('rating')
            review = request.POST.get('review')
            if OrderItem.objects.filter(order__user=request.user,order__order_status='DELIVERED',product_variant__product_id = product_id).exists():
                ProductReview.objects.create(user=request.user,product_id=product_id,rating=rating,review=review)
                messages.success(request, 'Review added successfully!')

        return redirect('product_app:product_view', product_id=product_id)
        
    else:
        return redirect('auth_app:login')

def review_view(request,product_id):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        product = Product.objects.get(id=product_id)
        reviews = ProductReview.objects.filter(product=product).order_by('-created_at')
        avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        avg_rating = round(avg_rating,1) if avg_rating else 0

        return render(request, 'user/reviews.html', {
            'product': product,
            'reviews': reviews,
            'avg_rating': avg_rating,
        })
    else:
        return redirect('auth_app:login')
