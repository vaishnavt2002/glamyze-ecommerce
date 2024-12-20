from django.shortcuts import render,redirect
from datetime import datetime
from .models import *
from PIL import Image
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
import re


# Create your views here.
@never_cache
def banner_view(request):
    banners = Banner.objects.all()
    return render(request,'my_admin/banners.html',{'banners':banners})

def validate_image_format(image,image_name):
            try:
                with Image.open(image) as img:
                    if img.format.lower() not in ['png', 'jpg', 'jpeg']:
                        return f"{image_name} must be a PNG or JPG file."
                    else:
                        return None
            except Exception:
                    return f"{image_name} is not a valid image file."
            
@never_cache
def add_banner(request):
    if request.user.is_superuser:    
        if request.method == 'POST':
            errors = []
            name = request.POST.get('name')
            description = request.POST.get('description')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            banner_type = request.POST.get('banner_type')
            image = request.FILES['banner_image']
            error = validate_image_format(image,'Banner image')
            if error:
                 errors.append(error)
            is_active = True if request.POST.get('is_active') else False  

            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
                end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            except ValueError:
                return redirect('banner_management:add_banner')
            
            if  not re.match(r'^[A-Za-z\s]+$',name):
                errors.append('Name must contain only letters and spaces')
            if len(name)<3:
                errors.append('Name should atleast contain 2 letters')
            if len(name)>25:
                errors.append('Name should atmost contain 25 letters')
            if  not re.match(r'^[A-Za-z\s.]+$',description):
                errors.append('Description must contain only letters and spaces')
            if len(description)<5 and len(description)>30:
                errors.append('Description should atleast contain 5 and atmost 30 letters')
            
            if start_date and start_date.date() < datetime.today().date():
                errors.append('Start date must be today or a future date.')

            if end_date and start_date and end_date < start_date:
                errors.append('End date must be greater than or equal to the start date.')
            if errors:
                 context ={
                      'name':name,
                      'start_date':start_date,
                      'end_date':end_date,
                      'description':description,
                      'errors':errors
                 }
                 return render(request,'my_admin/add_banner.html',context)

            banner = Banner(
                name=name.strip(),
                description=description.strip(),
                start_date=start_date,
                end_date=end_date,
                image=image,
                is_active=is_active
            )
            if banner_type == 'hero':
                 banner.banner_type = Banner.Type.HERO
            banner.save()
            return redirect('banner_management:banner_view') 
        else:
            return render(request,'my_admin/add_banner.html')    
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')
    
@never_cache
def edit_banner(request,banner_id):
    if request.user.is_superuser:
        banner = Banner.objects.get(id=banner_id)

        if request.method == 'POST':
            errors = []
            name = request.POST.get('name')
            description = request.POST.get('description')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            banner_type = request.POST.get('banner_type')
            image = request.FILES.get('banner_image')
            if image:
                error = validate_image_format(image,'Banner image')
                if error:
                    errors.append(error)

            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
                end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            except ValueError:
                return redirect('banner_management:add_banner')
            
            if  not re.match(r'^[A-Za-z\s]+$',name):
                errors.append('Name must contain only letters and spaces')
            if len(name)<3:
                errors.append('Name should atleast contain 2 letters')
            if len(name)>25:
                errors.append('Name should atmost contain 25 letters')
            if  not re.match(r'^[A-Za-z\s.]+$',description):
                errors.append('Description must contain only letters and spaces')
            if len(description)<5:
                errors.append('Description should atleast contain 5 letters')

            if end_date and start_date and end_date < start_date:
                errors.append('End date must be greater than or equal to the start date.')
            if errors:
                 context ={
                     
                      'errors':errors,
                      'banner':banner
                 }
                 
                 return render(request,'my_admin/edit_banner.html',context)
            banner.name = name.strip()
            banner.description = description.strip()
            banner.start_date = start_date
            banner.end_date = end_date
            if image:
                 banner.image.delete()
                 banner.image = image
            
            if banner_type == 'hero':
                 banner.banner_type = Banner.Type.HERO
            banner.save()
            return redirect('banner_management:banner_view') 
        else:
            banner = Banner.objects.get(id=banner_id)
            return render(request,'my_admin/edit_banner.html',{'banner':banner})    
    elif request.user.is_authenticated:
        if request.user.is_block:
            return redirect('auth_app:logout')
        return redirect('auth_app:home')
    else:
        return redirect('auth_app:login')


@never_cache
def activate_banner(request, banner_id):
    if request.user.is_superuser:
        if request.method == "POST":
            banner = Banner.objects.get(id=banner_id)
            banner.is_active = not banner.is_active
            banner.save()
            return JsonResponse({'status': 'success', 'is_listed': banner.is_active})
        elif request.user.is_authenticated:
            if request.user.is_block:
                return redirect('auth_app:logout')
            return redirect('auth_app:home')
        else:
            return redirect('auth_app:login')
    return JsonResponse({'status': 'error'}, status=400)
     
