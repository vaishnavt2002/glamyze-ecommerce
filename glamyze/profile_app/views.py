from django.shortcuts import render
from address_app.models import *
from auth_app.models import *
from django.utils import timezone
from datetime import timedelta
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from auth_app.validation import *
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.cache import never_cache


# Create your views here.
@never_cache
def profile_view(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    # Check if the user is authenticated
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')  
        address = Address.objects.filter(user=request.user).first()
        context = {'address':address}
        return render(request,'user/profile_management.html',context)
        
    else:
        return redirect('auth_app:login')
    

def send_otp(request,email):
    otp=random.randint(100000,999999)
    request.session['otp']=str(otp)
    expiry_time = timezone.now() + timedelta(minutes=3)
    request.session['otp_expiry'] = expiry_time.timestamp()
    subject = 'One Time Password'
    message = 'Your OTP to create account in Glamyze is  ' + str(otp)
    from_email = 'glamyze2024@gmail.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def email_otp(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    # Check if the user is authenticated
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')  
        email = request.session.get('email_change')
        try:
            send_otp(request,email)
        except Exception:
            return redirect('profile_app:profile_view')
        print('working')
        return redirect('profile_app:email_otp_verification')
        
    else:
        return redirect('auth_app:login')
    

def user_otp_resend(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        email = request.session['email_change']
        try:
            send_otp(request,email)
        except Exception:
            return redirect('profile_app:profile_view')
        return redirect('profile_app:email_otp')
    else:
        return redirect('auth_app:login')

@never_cache
def email_otp_verification(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    # Check if the user is authenticated
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')  
        if request.POST:
            if 'otp' in request.session and 'otp_expiry' in request.session:
                expiry = request.session['otp_expiry']
                otp = request.POST['otp']
                print(timezone.now().timestamp())
                if timezone.now().timestamp() > expiry:
                    return render(request, 'user/email_otp.html', {"errors": ["OTP has expired. Please request a new one."]})

                if otp == request.session['otp']:
                    email = request.session['email_change']
                    user = CustomUser.objects.get(email=request.user.email)
                    user.email = email
                    user.username = email
                    user.save()
                    del request.session['otp']
                    del request.session['otp_expiry']
                    del request.session['email_change']
                    return render(request, 'user/email_otp.html', {"change_success": True})
                else:
                    return render(request, 'user/email_otp.html', {"errors": ["Invalid OTP. Please try again."]})

        return render(request, 'user/email_otp.html')
        
    else:
        return redirect('auth_app:login')
    

@never_cache
def edit_profile(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    # Check if the user is authenticated
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')  
        user_data = CustomUser.objects.get(id=request.user.id)
        if request.POST:
            email = request.POST.get('email')
            phone_number = request.POST.get('phone')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            errors = []
            if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?$', email):
                errors.append('Invalid email format')
            if len(first_name)<2 or not re.match(r'^[A-Za-z\s]+$', first_name):
                errors.append("First name should be at least 2 characters and only contain letters.")
            if  not re.match(r'^[A-Za-z\s]+$', last_name):
                errors.append("Last name should only contain letters.")
            if not phone_number.isdigit() or len(phone_number) != 10 or not phone_number.startswith(('4','5','6', '7', '8', '9')):
                errors.append('Phone number is in invalid format')
            if errors:
                context = {'errors':errors,
                           'email':email,
                           'phone_number':phone_number,
                           'first_name':first_name,
                           'last_name':last_name}
                return render(request,'user/edit_profile.html',context)
            
            user_data.phone_number = phone_number
            user_data.first_name = first_name.strip()
            user_data.last_name = last_name.strip()
            user_data.save()
            if email != user_data.email:
                request.session['email_change'] = email
                user_data.refresh_from_db()
                if CustomUser.objects.filter(email=email):
                    return render(request,'user/edit_profile.html',{'user_data':user_data,'exist':True})
                else:
                    return render(request,'user/edit_profile.html',{'user_data':user_data,'email_change':True})
            else:
                return redirect('profile_app:profile_view')
        return render(request,'user/edit_profile.html',{'user_data':user_data})
        
    else:
        return redirect('auth_app:login')
    
@never_cache
def change_password(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        if request.POST:
            errors=[]
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if not check_password(current_password, request.user.password):
                errors.append('Current Password is wrong')

            if new_password != confirm_password:
                errors.append('new password and confirm password not matching')
            
            if current_password == new_password:
                errors.append('new password and old password are same')
            password_errors = Validation.password_validation(new_password)
            if password_errors:
                errors.extend(password_errors)
            if errors:
                return render(request,'user/change_password.html',{'errors':errors})

            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            return render(request,'user/change_password.html',{'success':True})

        return render(request,'user/change_password.html')
    else:
        return redirect('auth_app:login')