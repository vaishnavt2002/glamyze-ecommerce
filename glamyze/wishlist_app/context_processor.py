from .models import Wishlist
from django.db.models import Count

def wishlist_total(request):
    if request.user.is_authenticated:
        cart = Wishlist.objects.filter(user=request.user).first()
        if cart:
            total_items = cart.wishlistitem_set.aggregate(total=Count('id'))['total'] or 0
        else:
            total_items = 0
    else:
        total_items = 0
    return {'wishlist_total_items':total_items}