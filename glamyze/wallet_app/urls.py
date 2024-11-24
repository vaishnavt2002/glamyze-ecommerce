from django.urls import path,include
from . import views
app_name = 'wallet_app'
urlpatterns = [
    path('wallet/',views.wallet_view,name='wallet_view')
]

