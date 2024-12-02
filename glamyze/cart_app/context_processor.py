from .models import Cart
from django.db.models import Count

def cart_total(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            total_items = cart.items.aggregate(total=Count('id'))['total'] or 0
        else:
            total_items = 0
    else:
        total_items = 0
    return {'total_items':total_items}