from django.shortcuts import render,redirect,HttpResponse
from . validation import Validation
from django.core.mail import send_mail
import random
from . models import *
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout


def validate_data(email,phonenumber,password,confirm_password,fname,lname):
    errors=[]
    if Validation.email_validation(email):
        errors.append('Invalid email format')
    if Validation.phone_validation(phonenumber):
        errors.append('Invalid Phone number format')
    if Validation.name_validation(fname):
        errors.append('Invalid first name')
    if Validation.name_validation(lname):
        errors.append('Invalid last name')
    password_errors = Validation.password_validation(password)
    if password_errors:
        errors.extend(password_errors)
    if password != confirm_password:
        errors.append('password is not matching')
    return errors

def user_signup(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    if request.POST:
        email = request.POST.get('email')
        phonenumber = request.POST.get('phonenumber')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        errors = validate_data(email,phonenumber,password,confirm_password,fname,lname)
        if errors:
                context={'errors':errors,'email':email,'phonenumber':phonenumber,'first_name':fname,'last_name':lname}
                return render(request,'auth_app/signup.html',context)
        else:
            if CustomUser.objects.filter(email=email).exists():
                user=CustomUser.objects.get(email=email)
                if user.is_active == True:
                    return redirect('auth_app:login')
                else:
                    user.set_password(password)
                    user.first_name = fname
                    user.last_name = lname
                    user.save()
            else:
                CustomUser.objects.create_user(username=email,email=email,password=password,first_name=fname,last_name=lname,is_active=False)
            try:
                send_otp(request,email)
            except Exception:
                return render(request,'auth_app/signup.html',{"errors":['Email sending failed. Try again later']})
            request.session['email'] = email
            print(request.session['otp_expiry'])
            return redirect('auth_app:otp')
    return render(request,'auth_app/signup.html')

def user_otp_verification(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    if request.POST:
        if 'otp' in request.session and 'otp_expiry' in request.session:
            expiry = request.session['otp_expiry']
            otp = request.POST['otp']
            print(timezone.now().timestamp())
            if timezone.now().timestamp() > expiry:
                return render(request, 'auth_app/otp.html', {"errors": ["OTP has expired. Please request a new one."]})

            if otp == request.session['otp']:
                email = request.session['email']
                user = CustomUser.objects.get(email=email)
                user.is_active = True
                user.save()
                del request.session['otp']
                del request.session['otp_expiry']
                messages.success(request, 'Signup successful! You can now log in.')
                return redirect('auth_app:login')
            else:
                return render(request, 'auth_app/otp.html', {"errors": ["Invalid OTP. Please try again."]})

    return render(request, 'auth_app/otp.html')

    
def user_otp_resend(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    email = request.session['email']
    try:
        send_otp(request,email)
    except Exception:
        return render(request,'auth_app/signup.html',{"errors":['Email sending failed. Try again later']})
    return redirect('auth_app:otp')
            
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

def user_login(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    elif request.user.is_authenticated:
        return redirect('auth_app:home')
    if request.POST:
        email=request.POST.get('email')
        password=request.POST.get('password')
        try:
            user_data = CustomUser.objects.get(email=email)
        except Exception:
            return render(request,'auth_app/login.html',{'error':'invalid username or password'})
        if not user_data.is_active:
            return render(request,'auth_app/login.html',{'error':'You are blocked by admin.'})
        user=authenticate(request,email=email,password=password)
        print(user)
        if user is not None:
            login(request,user)
            if request.user.is_superuser:
                return redirect('admin_app:admin_dashboard')
            else:
                return redirect('auth_app:home')
        else:
            return render(request,'auth_app/login.html',{'error':'invalid username or password'})
    return render(request,'auth_app/login.html')

def home(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    elif request.user.is_authenticated:
        return render(request,'index.html')

def user_logout(request):
    if request.user.is_authenticated:
        logout(request)  # Logs out the user
    return redirect('auth_app:login')