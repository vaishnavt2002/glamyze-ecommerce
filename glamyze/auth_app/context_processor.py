from product_app.models import *

def category_load(request):
    categories = Category.objects.exclude(is_listed=False).order_by('id')
    return {'categories_load':categories}