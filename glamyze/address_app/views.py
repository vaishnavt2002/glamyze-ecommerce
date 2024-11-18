from django.shortcuts import render,redirect,get_object_or_404
from auth_app.models import *
from . models import *
from django.views.decorators.cache import never_cache
import re

# Create your views here.
@never_cache
def account_management(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return render(request,'user/user_dashboard.html')
    else:
        return redirect('auth_app:login')
    
@never_cache
def address_view(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')

    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        addresses = Address.objects.filter(user=request.user)
        if request.POST:
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            pincode = request.POST.get('pincode')
            locality = request.POST.get('locality')
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            landmark = request.POST.get('landmark')
            address_type = request.POST.get('addressType')
            alternate_phone = request.POST.get('alternate_phone')
            errors = []
            if  not re.match(r'^[A-Za-z\s]+$',name):
                errors.append('Name must contain only letters and spaces')
            if len(name)<2:
                errors.append('Name should atleast contain 2 letters')
            if not phone.isdigit() or len(phone) != 10 or not phone.startswith(('4','5','6', '7', '8', '9')):
                errors.append('Phone number is in invalid format')
            if not re.match(r'^[A-Za-z\s]+$',city):
                errors.append('City should only contain letters and spaces')
            if not re.match(r'^[A-Za-z\s]+$',state):
                errors.append('State should only contain letters and spaces')
            if alternate_phone:
                if not phone.isdigit() or len(phone) != 10 or not phone.startswith(('4','5','6', '7', '8', '9')):
                    errors.append('Alternate phone number is in invalid format')
            if not pincode.isdigit() or len(pincode) != 6 or  pincode.startswith('0'):
                errors.append('Pincode is wrong')
            if errors:
                context = {
                    'addresses':addresses,
                    'name':name,
                    'phone':phone,
                    'pincode':pincode,
                    'locality':locality,
                    'address':address,
                    'city':city,
                    'state':state,
                    'landmark':landmark,
                    'address_type':address_type,
                    'alternate_phone':alternate_phone,
                    'errors':errors
                }
                return render(request,'user/address.html',context)
            
            address_obj =                                                                                                                                                                                                                                                           Address(
                user=request.user,
                    name=name.strip(),
                    phone=phone.strip(),
                    pincode=pincode.strip(),
                    locality=locality.strip(),
                    address=address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    landmark=landmark.strip(),
                    office_home=address_type
                    )
            address_obj.save()
        return render(request,'user/address.html',{'addresses':addresses})
    else:
        return redirect('auth_app:login')
    
@never_cache  
def update_address(request, address_id):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')

    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        
        address = get_object_or_404(Address, id=address_id)
        if request.user != address.user:
            return redirect('auth_app:logout')

        if request.method == 'POST':
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            pincode = request.POST.get('pincode')
            locality = request.POST.get('locality')
            address_data = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            landmark = request.POST.get('landmark')
            alternate_phone = request.POST.get('alternate_phone')
            landmark = landmark if landmark else None
            alternate_phone = alternate_phone if alternate_phone else None
            address_type = request.POST.get('addressType')
            
            errors = []
            if  not re.match(r'^[A-Za-z\s]+$',name):
                errors.append('Name must contain only letters and spaces')
            if len(name)<2:
                errors.append('Name should atleast contain 2 letters')
            if not phone.isdigit() or len(phone) != 10 or not phone.startswith(('4','5','6', '7', '8', '9')):
                errors.append('Phone number is in invalid format')
            if not re.match(r'^[A-Za-z\s]+$',city):
                errors.append('City should only contain letters and spaces')
            if not re.match(r'^[A-Za-z\s]+$',state):
                errors.append('State should only contain letters and spaces')
            if alternate_phone:
                if not phone.isdigit() or len(phone) != 10 or not phone.startswith(('4','5','6', '7', '8', '9')):
                    errors.append('Alternate phone number is in invalid format')
            if not pincode.isdigit() or len(pincode) != 6 or  pincode.startswith('0'):
                errors.append('Pincode is wrong')
            if errors:
                return render(request, 'user/edit_address.html', {'address': address,'errors':errors})

            address.name = name.strip()
            address.phone = phone.strip()
            address.pincode = pincode.strip()
            address.locality = locality.strip()
            address.address = address_data.strip()
            address.city = city.strip()
            address.state = state.strip()
            landmark = landmark
            alternate_phone = alternate_phone
            address.landmark = landmark.strip() if landmark else None
            address.alternate_phone = alternate_phone.strip() if alternate_phone else None
            address.office_home = address_type
            address.save()
            return redirect('address_app:address_view') 
        return render(request, 'user/edit_address.html', {'address': address})

    else:
        return redirect('auth_app:login')
    
def delete_address(request,address_id):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')

    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        address = get_object_or_404(Address, id=address_id)
        if request.user != address.user:
            return redirect('auth_app:logout')
        address.delete()
        return redirect('address_app:address_view')
    else:
        return redirect('auth_app:login')




