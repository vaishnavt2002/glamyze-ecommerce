from django.contrib import admin
from django.urls import path
from . import views

app_name = 'auth_app'

urlpatterns = [
    path('',views.user_login,name="login"),
    path('signup/',views.user_signup,name="signup"),
    path('otp-verification/',views.user_otp_verification,name="otp"),
    path('otp-resend/',views.user_otp_resend,name='resend-otp'),
    path('home/',views.home,name='home'),
    path('logout/',views.user_logout,name='logout')
]