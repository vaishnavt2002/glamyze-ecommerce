from django.urls import path,include
from . import views


app_name = 'profile_app'

urlpatterns = [
    path('profile/',views.profile_view,name='profile_view'),
    path('profile/edit/',views.edit_profile,name='edit_profile'),
    path('profile/email/otp-send/',views.email_otp,name='email_otp'),
    path('profile/email/verification/',views.email_otp_verification,name='email_otp_verification'),
    path('profile/email/resend/',views.user_otp_resend,name='user_otp_resend'),
    path('profile/change-password',views.change_password,name='change_password')
]
