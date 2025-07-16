from django.shortcuts import render,redirect
from . validation import Validation
from django.core.mail import send_mail
import random
from . models import *
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate,login,logout
from product_app.models import *
from django.views.decorators.cache import never_cache
from allauth.socialaccount.models import SocialAccount
from django.core.paginator import Paginator
from django.db.models import Prefetch,Count
from django.db.models import Q,Sum,Min
from banner_management.models import *
from wallet_app.models import *
from decimal import Decimal




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

@never_cache
def user_signup(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')
 
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    if request.POST:
        email = request.POST.get('email')
        phonenumber = request.POST.get('phonenumber')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        referral_code = request.POST.get('referral_code')
        errors = validate_data(email,phonenumber,password,confirm_password,fname,lname)
        if errors:
                context={'errors':errors,'email':email,'phonenumber':phonenumber,'first_name':fname,'last_name':lname,'referral_code':referral_code}
                return render(request,'auth_app/signup.html',context)
        else:
            if CustomUser.objects.filter(email=email).exists():
                user=CustomUser.objects.get(email=email)
                if user.is_active == True:
                    return render(request,'auth_app/signup.html',{"account_exists":True})
                else:
                    user.set_password(password)
                    user.first_name = fname
                    user.last_name = lname
                    user.save()
            else:
                referred_by=None
                if referral_code:
                    try:
                        referred_by = CustomUser.objects.get(referral_code=referral_code)
                    except:
                        errors =['Invalid referral']
                        context={'errors':errors,'email':email,'phonenumber':phonenumber,'first_name':fname,'last_name':lname,'referral_code':referral_code}
                        return render(request,'auth_app/signup.html',context)

                CustomUser.objects.create_user(username=email,email=email,phone_number=phonenumber,password=password,first_name=fname,last_name=lname,is_active=False,referred_by=referred_by)
            try:
                send_otp(request,email)
            except Exception:
                return render(request,'auth_app/signup.html',{"errors":['Email sending failed. Try again later']})
            request.session['email'] = email
            return redirect('auth_app:otp')
    return render(request,'auth_app/signup.html')

@never_cache
def user_otp_verification(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')

    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    if request.POST:
        if 'otp' in request.session and 'otp_expiry' in request.session:
            expiry = request.session['otp_expiry']
            otp = request.POST['otp']
            if timezone.now().timestamp() > expiry:
                return render(request, 'auth_app/otp.html', {"errors": ["OTP has expired. Please request a new one."]})

            if otp == request.session['otp']:
                email = request.session['email']
                user = CustomUser.objects.get(email=email)
                user.is_active = True
                user.save()
                if user.referred_by:
                    wallet,created = Wallet.objects.get_or_create(user=user)
                    tranasaction = WalletTransaction(wallet=wallet,transaction_type='REFERRAL',amount=100)
                    tranasaction.save()
                    wallet.balance += Decimal(100.00)
                    wallet.save()
                    ref_wallet,created = Wallet.objects.get_or_create(user=user.referred_by)
                    tranasaction = WalletTransaction(wallet=ref_wallet,transaction_type='REFERRAL',amount=100)
                    tranasaction.save()
                    ref_wallet.balance += Decimal(100.00)
                    ref_wallet.save()
                del request.session['otp']
                del request.session['otp_expiry']
                del request.session['email']
                return render(request, 'auth_app/otp.html', {"signup_success": True})
            else:
                return render(request, 'auth_app/otp.html', {"errors": ["Invalid OTP. Please try again."]})

    return render(request, 'auth_app/otp.html')

@never_cache
def user_otp_resend(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')

    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
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

@never_cache
def user_login(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')
 
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    if request.POST:
        email=request.POST.get('email')
        password=request.POST.get('password')
        try:
            user_data = CustomUser.objects.get(email=email)
        except Exception:
            return render(request,'auth_app/login.html',{'error':'invalid username or password'})
        if  user_data.is_block:
            return render(request,'auth_app/login.html',{'error':'You are blocked by admin.'})
        if SocialAccount.objects.filter(user=user_data, provider='google').exists():
            return render(request, 'auth_app/login.html', {'error': 'This account is registered using Google. Please sign in with Google.'})
        if  not user_data.is_active:
            return render(request,'auth_app/login.html',{'error':'Your Sign up is incomplete'})
        user=authenticate(request,email=email,password=password)
        if user is not None:
            login(request,user)
            if request.user.is_superuser:
                return redirect('admin_app:admin_dashboard')
            else:
                return redirect('auth_app:home')
        else:
            return render(request,'auth_app/login.html',{'error':'invalid username or password'})
    return render(request,'auth_app/login.html')

@never_cache
def forgot_password(request):
    if request.POST:
        email = request.POST['email']
        if CustomUser.objects.filter(email=email,is_block=False).exists():
            user_data = CustomUser.objects.get(email=email)
            if SocialAccount.objects.filter(user=user_data, provider='google').exists():
                return render(request,'auth_app/enter_email.html',{"error":'Email id is used for Google sign in'})
            try:
                send_otp(request,email)
            except Exception:
                return render(request,'auth_app/enter_email.html',{"error":'Email sending failed. Try again later'})
            request.session['email']=email
            return redirect('auth_app:forgot_password_otp')
        else:
            return render(request,'auth_app/enter_email.html',{'error':'This is not a registered email id or You are blocked by admin'})

    return render(request,'auth_app/enter_email.html')

@never_cache
def user_otp_verification_forgotpassword(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')
    
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    if request.POST:
        if 'otp' in request.session and 'otp_expiry' in request.session:
            errors = []
            expiry = request.session['otp_expiry']
            otp = request.POST['otp']
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if timezone.now().timestamp() > expiry:
                return render(request, 'auth_app/forgotpassword_otp.html', {"errors": ["OTP has expired. Please request a new one."]})

            if otp == request.session['otp']:
                email = request.session['email']
                if password != confirm_password:
                    errors.append('password is not matching')
                password_errors = Validation.password_validation(password)
                if password_errors:
                    errors.extend(password_errors)
                if errors:
                    return render(request, 'auth_app/forgotpassword_otp.html',{'errors':errors})
                user=CustomUser.objects.get(email=email)
                user.set_password(password)
                user.save()
                del request.session['otp']
                del request.session['otp_expiry']
                return redirect('auth_app:login')
            else:
                return render(request, 'auth_app/forgotpassword_otp.html', {"errors": ["Invalid OTP. Please try again."]})
    return render(request,'auth_app/forgotpassword_otp.html')

@never_cache
def user_otp_resend_forgot(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')
     
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return redirect('auth_app:home')
    email = request.session['email']
    try:
        send_otp(request,email)
    except Exception:
        return render(request,'auth_app/enter_email.html',{"errors":['Email sending failed. Try again later']})
    return redirect('auth_app:forgot_password_otp')

@never_cache
def home(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')
     
    if request.user.is_authenticated:
        if SocialAccount.objects.filter(user=request.user, provider='google').exists() and request.user.is_block:
            return render(request,'user/index.html',{'blocked':True})
        if request.user.is_block:
            return redirect('auth_app:logout') 
        current_date = timezone.now().date()
        slider = Banner.objects.filter(
                    is_active=True,
                    start_date__lte=current_date,
                    end_date__gte=current_date
                )
        products = Product.objects.filter(is_listed=True)[0:8]
        products = Product.objects.filter(
            is_active=True,
            is_listed=True,
            subcategory__category__is_listed=True,
            subcategory__is_listed=True,
            productvariant__is_listed=True
        ).annotate(total_stock=Sum('productvariant__quantity')).distinct().order_by('id')[0:8]
        products = list(products)
        for product in products:
            variant = product.productvariant_set.first() if product.productvariant_set.exists() else None
            if variant:
                product.variant_price = variant.price
                # Calculate offer price if product has an active offer
                if product.offer and product.offer.is_active and product.offer.start_date<=current_date and product.offer.end_date>=current_date:
                    discount = product.offer.discount_percentage
                    product.offer_price = round(variant.price * (1 - discount / 100), 2)
                else:
                    product.offer_price = None
        return render(request,'user/index.html',{'products':products,'slider':slider})
    else:
        current_date = timezone.now().date()

        slider = Banner.objects.filter(
                    is_active=True,
                    start_date__lte=current_date,
                    end_date__gte=current_date
                )
        products = Product.objects.filter(is_listed=True)[0:8]
        products = Product.objects.filter(
            is_active=True,
            is_listed=True,
            subcategory__category__is_listed=True,
            subcategory__is_listed=True,
            productvariant__is_listed=True
        ).annotate(total_stock=Sum('productvariant__quantity'),variant_price=Min('productvariant__price')).distinct().order_by('id')[0:8]
        for product in products:
            variant = product.productvariant_set.first() if product.productvariant_set.exists() else None
            if variant:
                product.variant_price = variant.price
                if product.offer and product.offer.is_active and product.offer.start_date<=current_date and product.offer.end_date>=current_date:
                    discount = product.offer.discount_percentage
                    product.offer_price = round(variant.price * (1 - discount / 100), 2)
                else:
                    product.offer_price = None
        return render(request,'user/index.html',{'products':products,'slider':slider})
    
def google_home(request):
    return redirect('auth_app:home')


@never_cache
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('auth_app:home')

def about(request):
    return render(request,'user/about.html')

def contact(request):
    return render(request,'user/contact.html')