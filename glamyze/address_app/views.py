from django.shortcuts import render,redirect,get_object_or_404
from auth_app.models import *
from . models import *
# Create your views here.
def account_management(request):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard') 
    
    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        return render(request,'user/user_dashboard.html')
    else:
        return redirect('auth_app:login')
    

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
            address_obj =                                                                                                                                                                                                                                                           Address(
                user=request.user,
                    name=name,
                    phone=phone,
                    pincode=pincode,
                    locality=locality,
                    address=address,
                    city=city,
                    state=state,
                    landmark=landmark,
                    office_home=address_type
                    )
            address_obj.save()
        return render(request,'user/address.html',{'addresses':addresses})
    else:
        return redirect('auth_app:login')
    
def update_address(request, address_id):
    if request.user.is_superuser:
        return redirect('admin_app:admin_dashboard')

    if request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout') 
        address = get_object_or_404(Address, id=address_id)

        if request.method == 'POST':
            # Update each field with the form data
            address.name = request.POST.get('name')
            address.phone = request.POST.get('phone')
            address.pincode = request.POST.get('pincode')
            address.locality = request.POST.get('locality')
            address.address = request.POST.get('address')
            address.city = request.POST.get('city')
            address.state = request.POST.get('state')
            
            # Handle optional fields for landmark and alternate phone
            landmark = request.POST.get('landmark')
            alternate_phone = request.POST.get('alternate_phone')
            address.landmark = landmark if landmark else None
            address.alternate_phone = alternate_phone if alternate_phone else None
            
            # Update address type
            address.office_home = request.POST.get('addressType')
            
            # Save the updated address information
            address.save()

            return redirect('address_app:address_view')  # Update this URL name as needed

        # Render the form with the current address data
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
        address.delete()
        return redirect('address_app:address_view')
    else:
        return redirect('auth_app:login')




