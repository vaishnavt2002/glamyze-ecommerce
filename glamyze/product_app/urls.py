
from django.urls import path
from . import views

app_name = 'product_app'

urlpatterns = [
    path('shop/',views.shop,name='shop'),
    path('shop/<int:product_id>/view/',views.product_view,name='product_view'),
    path('shop/<int:product_id>/add-review/',views.product_review,name='product_review'),
    path('shop/<int:product_id>/reviews/',views.review_view,name='review_view')
]