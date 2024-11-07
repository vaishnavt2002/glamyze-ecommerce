
from django.urls import path
from . import views

app_name = 'cart_app'

urlpatterns = [
    path('shop/add-to-cart/',views.add_to_cart,name='add_to_cart'),
    path('shop/cart/',views.cart_view,name='cart_view'),
    path('shop/cart/<int:id>/delete',views.cart_item_delete,name='cart_item_delete')
    
]