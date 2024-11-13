from django.urls import path
from . import views

app_name = 'order_app'
urlpatterns = [
    path('proceed-to-checkout',views.proceed_to_checkout,name='proceed_to_checkout'),
    path('checkout/',views.checkout_view,name='checkout_view'),
    path('order-summary',views.order_summary,name='order_summary')
]