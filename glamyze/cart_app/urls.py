
from django.urls import path
from . import views

app_name = 'cart_app'

urlpatterns = [
    path('shop/add-to-cart/',views.add_to_cart,name='add_to_cart')
]