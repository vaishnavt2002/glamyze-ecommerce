from django.urls import path,include
from . import views
app_name='customer_management'

urlpatterns = [
    path('customers/',views.customer_details,name='customer_details'),
    path('customers/<int:user_id>/block-unblock/', views.block_unblock_user, name='block_unblock_user'),

]