from django.urls import path,include
from . import views

app_name = 'banner_management'

urlpatterns = [
   path('banners/',views.banner_view,name='banner_view'),
   path('banners/add/',views.add_banner,name='add_banner'),
   path('banner/<int:banner_id>/edit/',views.edit_banner,name='edit_banner'),
   path('banner/<int:banner_id>/list-unlist',views.activate_banner,name='activate_banner')
]