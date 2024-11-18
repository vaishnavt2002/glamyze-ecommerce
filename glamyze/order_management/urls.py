
from django.urls import path
from . import views

app_name = 'order_management'
urlpatterns = [
    path('orders/',views.order_view,name='order_view'),
    path('orders/<int:order_id>/details',views.order_detail,name='order_detail'),
    path('orders/<int:order_id>/update',views.order_update,name='order_update')
]