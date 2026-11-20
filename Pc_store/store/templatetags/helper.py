from django import template
from store.models import CartItem, Whishlist

register = template.Library()


# 1. Wishlist Count
@register.simple_tag
def get_wishlist_count(user):
    try:
        if not user or not user.is_authenticated:
            return 0
        return Whishlist.objects.filter(user=user).count()
    except Exception as e:
        print("Error in get_wishlist_count:", e)
        return 0


# 2. Cart Count (Total items in cart)
@register.simple_tag
def get_cart_count(user):
    try:
        if not user or not user.is_authenticated:
            return 0
        items = CartItem.objects.filter(user=user)
        total = 0
        for item in items:
            total += item.quantity
        return total
    except Exception as e:
        print("Error in get_cart_count:", e)
        return 0


# 3. Check if Product is in Wishlist
@register.simple_tag
def is_in_wishlist(user, product):
    try:
        if not user or not user.is_authenticated or not product:
            return False
        return Whishlist.objects.filter(user=user, product=product).exists()
    except Exception as e:
        print("Error in is_in_wishlist:", e)
        return False


# 4. Check if Product is in Cart
@register.simple_tag
def is_in_cart(user, product):
    try:
        if not user or not user.is_authenticated or not product:
            return False
        return CartItem.objects.filter(user=user, product=product).exists()
    except Exception as e:
        print("Error in is_in_cart:", e)
        return False


# 5. Cart Grand Total
@register.simple_tag
def get_cart_total(user):
    try:
        if not user or not user.is_authenticated:
            return 0
        items = CartItem.objects.filter(user=user)
        total = 0
        for item in items:
            total += item.product.product_price * item.quantity
        return total
    except Exception as e:
        print("Error in get_cart_total:", e)
        return 0


# 6. Multiply Filter (Quantity * Price)
@register.filter
def multiply(qty, price):
    try:
        return float(qty) * float(price)
    except Exception as e:
        print("Error in multiply:", e)
        return 0


# 7. Get All Categories for Navbar
@register.simple_tag
def get_categories():
    try:
        from store.models import Category
        return Category.objects.all()
    except Exception as e:
        print("Error in get_categories tag:", e)
        return []
