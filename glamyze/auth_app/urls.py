from django.contrib import admin
from django.urls import path
from . import views

app_name = 'auth_app'

urlpatterns = [
    path('',views.home,name='home'),
    path('login/',views.user_login,name="login"),
    path('signup/',views.user_signup,name="signup"),
    path('otp-verification/',views.user_otp_verification,name="otp"),
    path('otp-resend/',views.user_otp_resend,name='resend-otp'),
    path('logout/',views.user_logout,name='logout'),
    path('forgot-password/',views.forgot_password,name='forgot_password'),
    path('forgot-password/otp-verify/',views.user_otp_verification_forgotpassword,name='forgot_password_otp'),
    path('forgot-password/otp-verify/resend',views.user_otp_resend_forgot,name='user_otp_resend_forgot')
]