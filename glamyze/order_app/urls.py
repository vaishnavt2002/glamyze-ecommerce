from django.urls import path
from . import views

app_name = 'order_app'
urlpatterns = [
    path('proceed-to-checkout',views.proceed_to_checkout,name='proceed_to_checkout'),
    path('checkout/',views.checkout_view,name='checkout_view'),
    path('checkout/order-summary',views.order_summary,name='order_summary'),
    path('checkout/order-summary/confirm/',views.confirm_order,name='confirm_order'),
    path('account/orders/',views.order_view,name='order_view'),
    path('account/orders/<int:order_id>/order-details',views.order_details,name='order_details')
]