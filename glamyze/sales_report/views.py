from django.shortcuts import render
from order_app.models import *
from django.db.models import Sum,Count,Avg,F,Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import csv
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
# Create your views here.
def sales_view(request):
    date_filter = request.GET.get('date_filter', 'today')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    orders = Order.objects.exclude(Q(order_status='PENDING')|Q(order_status='FAILED')).prefetch_related('orderitem_set__product_variant__product','user').order_by('-created_at')
    today = timezone.now().date()
    if date_filter == 'today':
        orders = orders.filter(created_at__date=today)
    elif date_filter == 'week':
        week_start = today - timedelta(days=today.weekday())
        orders = orders.filter(created_at__date__gte=week_start)
    elif date_filter == 'month':
        orders = orders.filter(created_at__date__year=today.year, created_at__date__month=today.month)
    elif date_filter == 'custom' and start_date and end_date:
        orders = orders.filter(created_at__date__range=[start_date, end_date])

    # Apply price filters
    if min_price:
        orders = orders.filter(total_amount__gte=min_price)
    if max_price:
        orders = orders.filter(total_amount__lte=max_price)

    values = orders.aggregate(
        total_sales=Sum('total_amount'),
        total_orders=Count('id'),
        avg_order_value=Avg('total_amount')
    )

    # Calculate total discounts (both offer and coupon)
    total_discounts = Decimal('0.0')
    for order in orders:
        for item in order.orderitem_set.all():
            offer_discount = 0
            if item.offer_price is not None:
                offer_discount += (item.price - item.offer_price)*item.quantity
        coupon_discount = order.coupon.discount_amount if order.coupon else Decimal('0.0')
        total_discounts += offer_discount + coupon_discount

    # Handle Excel export
    if request.GET.get('export') == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Order ID', 'Date', 'Customer', 'Items', 'Subtotal', 
            'Offer Discount', 'Coupon Discount', 'Final Amount', 
            'Payment Method', 'Status'
        ])

        for order in orders:
            items = ', '.join([
                f"{item.product_variant.product.product_name} ({item.quantity})"
                for item in order.orderitem_set.all()
            ])
            
            offer_discount = sum(
                (item.price - item.offer_price) * item.quantity
                for item in order.orderitem_set.all()
                if item.offer_price is not None
            )
            
            coupon_discount = order.coupon.discount_amount if order.coupon else Decimal('0.0')
            
            writer.writerow([
                order.id,
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                order.user.email,
                items,
                sum(item.price * item.quantity for item in order.orderitem_set.all()),
                offer_discount,
                coupon_discount,
                order.total_amount,
                order.payment_method,
                order.order_status
            ])
        return response
    if request.GET.get('export') == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=30, bottomMargin=30)
        
        # Define table headings
        data = [['Order ID', 'Date', 'Customer', 'Items', 'Subtotal', 'Offer Discount', 'Coupon Discount', 'Final Amount']]

        # Get styles for wrapping
        styles = getSampleStyleSheet()
        normal_style = styles['BodyText']
        normal_style.wordWrap = 'CJK'  # For better text wrapping

        # Add order data to the table with wrapping
        for order in orders:
            items = ', '.join([
                f"{item.product_variant.product.product_name} ({item.quantity})"
                for item in order.orderitem_set.all()
            ])
            offer_discount = sum(
                (item.price - item.offer_price) * item.quantity
                for item in order.orderitem_set.all()
                if item.offer_price is not None
            )
            coupon_discount = order.coupon.discount_amount if order.coupon else 0
            
            data.append([
                order.id,
                order.created_at.strftime('%Y-%m-%d'),
                order.user.email,
                Paragraph(items, normal_style),  # Wrap items text
                f"Rs.{sum(item.price * item.quantity for item in order.orderitem_set.all()):.2f}",
                f"Rs.{offer_discount:.2f}",
                f"Rs.{coupon_discount:.2f}",
                f"Rs.{order.total_amount:.2f}"
            ])

        # Create the table and set column widths
        col_widths = [60, 80, 120, 200, 80, 80, 80, 80]  # Adjust as needed
        table = Table(data, colWidths=col_widths)

        # Table styling
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])
        table.setStyle(style)

        # Build and return the PDF
        pdf.build([table])
        buffer.seek(0)
        response.write(buffer.read())
        buffer.close()
        return response

    # Existing logic for HTML and Excel export...


    context = {
        'orders': orders,
        'total_sales': values['total_sales'] or 0,
        'total_orders': values['total_orders'] or 0,
        'avg_order_value': values['avg_order_value'] or 0,
        'total_discounts': total_discounts
    }

    return render(request, 'my_admin/sales_report.html', context)