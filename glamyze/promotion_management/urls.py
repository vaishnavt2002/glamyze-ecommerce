
from django.urls import path
from . import views

app_name = 'promotion_management'
urlpatterns = [
    path('offers/',views.offer_view,name='offer_view'),
    path('offers/add/',views.add_offer,name='add_offer'),
    path('offers/<int:offer_id>/activate-deactvate/',views.activate_offer,name='activate_offer'),
    path('offers/<int:offer_id>/delete',views.delete_offer,name='delete_offer'),
    path('offers/<int:offer_id>/edit/',views.edit_offer,name='edit_offer'),
    path('coupons/',views.coupon_view,name='coupon_view'),
    path('coupons/add',views.add_coupon,name='add_coupon'),
    path('coupons/<int:coupon_id>/edit',views.edit_coupon,name='edit_coupon')
]

