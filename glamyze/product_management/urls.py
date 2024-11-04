from django.urls import path,include
from . import views

app_name = 'product_management'
urlpatterns = [
    path('products/',views.product_details,name='product_details'),
    path('products/add/',views.product_add,name='product_add'),
    path('products/add-size/',views.product_size,name='product_size'),
    path('products/add-size-add',views.size_add,name='size_add'),
    path('products/<int:product_id>/block-unblock/', views.list_unlist_product, name='list_unlist_product'),
    path('products/<int:product_id>/inactive_product/',views.inactive_product,name='inactive_product'),
    path('products/<int:product_id>/edit/',views.product_edit,name='product_edit'),
    path('products/<int:product_id>/varients',views.product_varient_management,name='product_varient_management'), 
    path('products/<int:product_id>/add-quantity',views.product_add_quantity,name='product_add_quantity'),
    path('products/varient_management-post',views.product_varient_management_post,name='product_varient_management_post')
]