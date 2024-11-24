from django.urls import path,include
from . import views
app_name = 'wallet_app'
urlpatterns = [
    path('wallet/',views.wallet_view,name='wallet_view'),
    path('wallet/add-amount/',views.add_amount,name='add_amount'),
    path('wallet/payment-success',views.payment_success,name='payment_success'),
    path('wallet/payment-failed',views.payment_failure,name='payment_failure')
]

