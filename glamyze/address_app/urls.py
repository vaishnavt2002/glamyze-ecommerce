from django.urls import path,include
from . import views


app_name = 'address_app'

urlpatterns = [
    path('accounts/',views.account_management, name='account_management')
]
