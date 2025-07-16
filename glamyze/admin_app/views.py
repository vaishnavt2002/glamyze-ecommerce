from django.shortcuts import render,redirect
from django.views.decorators.cache import never_cache
from order_app.models import *
from django.db.models import Count,Sum,Q,F,Value
from django.db.models.functions import Concat
import calendar
from datetime import datetime
from django.utils import timezone


# Create your views here.


def admin_home(request):
    if request.user.is_superuser:
        filter_type = request.GET.get('filter', 'daily')
        current_year = timezone.now().year
        current_date = timezone.now().date()
        labels = []
        sales = []
        if filter_type == 'monthly':
            sales_data = (Order.objects.filter(created_at__year=current_year).exclude(Q(order_status='PENDING')|Q(order_status='FAILED')).values('created_at__month').annotate(total_sales=Count('id')).order_by('created_at__month'))
            months = list(range(1, timezone.now().month+1))
            monthly_sales = {month: 0 for month in months}

            for sale in sales_data:
               monthly_sales[sale['created_at__month']] = sale['total_sales']


            labels = [calendar.month_name[month] for month in months]
            sales = [monthly_sales[month] for month in months]


        elif filter_type == 'daily':
            dates = [(current_date - timezone.timedelta(days=i)) for i in range(7)]  # List of last 7 days
            sales_data = (Order.objects.filter(created_at__date__gte=current_date - timezone.timedelta(days=7)).exclude(Q(order_status='PENDING')|Q(order_status='FAILED'))
                          .values('created_at__date')
                          .annotate(total_sales=Count('id'))
                          .order_by('created_at__date'))
            daily_sales = {date: 0 for date in dates}



           # Fill actual sales data
            for sale in sales_data:
               daily_sales[sale['created_at__date']] = sale['total_sales']


            labels = [str(date) for date in dates]  # Convert dates to strings for the labels
            sales = [daily_sales[date] for date in dates]


        else:
            sales_data = (Order.objects.filter(created_at__year__gte=current_year - 4).exclude(Q(order_status='PENDING')|Q(order_status='FAILED'))
                         .values('created_at__year')
                         .annotate(total_sales=Count('id'))
                         .order_by('created_at__year'))
            years = list(range(current_year - 4, current_year + 1))
            yearly_sales = {year: 0 for year in years}
            for sale in sales_data:
               yearly_sales[sale['created_at__year']] = sale['total_sales']


            labels = [str(year) for year in years]
            sales = [yearly_sales[year] for year in years]


       
        top_products = (OrderItem.objects.exclude(order__order_status__in=['PENDING', 'FAILED']).values('product_variant__product__product_name').annotate(total_quantity=Sum('quantity'))
                        .order_by('-total_quantity')[:10])


        top_subcategories = (
                           OrderItem.objects.exclude(order__order_status__in=['PENDING', 'FAILED'])
                           .values(
                               category_and_subcategory=Concat(
                                   F('product_variant__product__subcategory__category__category_name'),
                                   Value('--'),
                                   F('product_variant__product__subcategory__subcategory_name')
                                )
                            )
                           .annotate(total_quantity=Sum('quantity'))
                           .order_by('-total_quantity')[:10]
                        )
        context = {
           'labels': labels,
           'sales': sales,
           'top_products': top_products,
           'top_subcategories': top_subcategories,
           'filter_type': filter_type,
        }
        return render(request, 'my_admin/dashboard.html', context)
    elif request.user.is_authenticated:
        if request.user.is_block:
           return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
