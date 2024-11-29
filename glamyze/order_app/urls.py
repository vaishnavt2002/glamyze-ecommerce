from django.urls import path
from . import views

app_name = 'order_app'
urlpatterns = [
    path('proceed-to-checkout',views.proceed_to_checkout,name='proceed_to_checkout'),
    path('checkout/',views.checkout_view,name='checkout_view'),
    path('checkout/order-summary',views.order_summary,name='order_summary'),
    path('checkout/order-summary/confirm/',views.confirm_order,name='confirm_order'),
    path('account/orders/',views.order_view,name='order_view'),
    path('account/orders/<int:order_id>/order-details/',views.order_details,name='order_details'),
    path('payment_success/',views.payment_success,name='payment_success'),
    path('payment-failed/',views.payment_failure,name='payment_failure'),
    path('checkout/apply-coupon/',views.apply_coupon,name='apply_coupon'),
    path('account/orders/<int:order_id>/cancel/',views.cancel_order,name='cancel_order'),
    path('account/orders/item/return/',views.return_product,name='return_product'),
    path('account/orders/<int:order_id>/invoice/',views.generate_invoice_pdf,name='generate_invoice_pdf'),
    path('account/orders/<int:order_id>/continue-payment/',views.continue_payment,name='continue_payment')


]