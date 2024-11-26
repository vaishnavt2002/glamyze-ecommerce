
from django.urls import path
from . import views

app_name = 'order_management'
urlpatterns = [
    path('orders/',views.order_view,name='order_view'),
    path('orders/<int:order_id>/details/',views.order_detail,name='order_detail'),
    path('orders/<int:order_id>/update/',views.order_update,name='order_update'),
    path('orders/<int:order_id>/cancel/',views.order_cancellation,name='order_cancellation'),
    path('orders/<int:orderitem_id>/approve/',views.order_return_approve,name='order_return_approve'),
    path('orders/<int:orderitem_id>/reject/',views.order_return_reject,name='order_return_reject')
]