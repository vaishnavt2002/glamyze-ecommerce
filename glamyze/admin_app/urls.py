from django.urls import path,include
from auth_app import views
from . import views

app_name = 'admin_app'

urlpatterns = [
    path('dashboard/',views.admin_home,name='admin_dashboard'),
    
]