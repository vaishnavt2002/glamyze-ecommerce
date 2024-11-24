from django.urls import path
from . import views


app_name = 'sales_report'
urlpatterns = [
    path('sales/',views.sales_view,name='sales_view')
]