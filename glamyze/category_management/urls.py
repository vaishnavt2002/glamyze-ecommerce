from django.urls import path
from . import views

app_name = 'category_management'
urlpatterns = [
    path('category/',views.category_view,name='category_view'),
    path('category/update/',views.category_update,name='category_update'),
    path('category/<int:id>/list-unlist/',views.categories_list_unlist,name='categories_list_unlist'),
    path('category/subcategory/update/',views.subcategory_update,name='subcategory_update'),
    path('category/subcategory/<int:id>/list-unlist/',views.subcategories_list_unlist,name='subcategories_list_unlist'),
    path('category/subcategory/add',views.subcategory_add,name='subcategory_add'),
    path('category/offer/apply/',views.category_offer_update,name='category_offer_update'),
    path('subcategory/offer/apply/',views.subcategory_offer_update,name='subcategory_offer_update'),
    path('category/offer/<int:category_id>/delete/',views.category_offer_delete,name='category_offer_delete'),
    path('subcategory/offer/<int:subcategory_id>/delete/',views.subcategory_offer_delete,name='subcategory_offer_delete')

]