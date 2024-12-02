from django.urls import path,include
from . import views
app_name = 'wishlist_app'
urlpatterns = [
    path('wishlist/',views.wishlist_view,name='wishlist_view'),
    path('wishlist/<int:productvariant_id>/add/',views.add_to_wishlist,name='add_to_wishlist'),
    path('wishlist/<int:wishlistitem_id>/delete/',views.delete_from_wishlist,name='delete_from_wishlist'),
    path('wishlist/<int:wishlistitem_id>/add-to-cart/',views.add_to_cart,name='add_to_cart')
]