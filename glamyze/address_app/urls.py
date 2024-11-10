from django.urls import path,include
from . import views


app_name = 'address_app'

urlpatterns = [
    path('accounts/',views.account_management, name='account_management'),
    path('address/',views.address_view,name='address_view'),
    path('address/<int:address_id>/edit/',views.update_address,name='update_address'),
    path('address/<int:address_id>/delete/',views.delete_address,name='delete_address'),
]
