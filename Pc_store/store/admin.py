from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Whishlist, CartItem, Address, Order, OrderItem, Enquiry

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'category_slug', 'category_created_at')
    search_fields = ('category_name', 'category_slug')
    prepopulated_fields = {'category_slug': ('category_name',)}
    list_filter = ('category_created_at',)
    ordering = ('id',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'product_name', 'product_category', 'part_type', 'product_price', 'product_quantity_in_stock')
    search_fields = ('product_name', 'product_slug', 'product_description')
    prepopulated_fields = {'product_slug': ('product_name',)}
    list_filter = ('product_category', 'part_type', 'product_created_at')
    list_editable = ('part_type', 'product_price', 'product_quantity_in_stock')
    ordering = ('id',)

    def image_preview(self, obj):
        if obj.product_image:
            return format_html('<img src="{}" width="48" height="48" style="object-fit:cover; border-radius:6px; border:1px solid #ddd;" />', obj.product_image.url)
        return format_html('<span style="color:#999;">No image</span>')
    image_preview.short_description = 'Photo'


class WhishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__product_name')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Whishlist, WhishlistAdmin)


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'user', 'session_key', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__product_name', 'user__username')


admin.site.register(CartItem, CartItemAdmin)


class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'city', 'state', 'postal_code', 'address_type', 'created_at')
    list_filter = ('state', 'address_type', 'created_at')
    search_fields = ('user__username', 'full_name', 'phone', 'city', 'state', 'postal_code')


admin.site.register(Address, AddressAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'user',
        'total_amount',
        'payment_method',
        'status',
        'razorpay_order_id',
        'razorpay_payment_id',
        'created_at'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = (
        'order_id',
        'user__username',
        'shipping_address_text',
        'razorpay_order_id',
        'razorpay_payment_id',
        'razorpay_signature',
        'cancellation_reason',
        'exchange_reason'
    )
    readonly_fields = ('order_id', 'created_at', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'status', 'total_amount', 'created_at')
        }),
        ('Delivery & Address', {
            'fields': ('address', 'shipping_address_text')
        }),
        ('Payment & Razorpay Details', {
            'fields': ('payment_method', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
        ('Cancellation & Exchange', {
            'fields': ('cancellation_reason', 'exchange_reason')
        }),
    )
    inlines = [OrderItemInline]


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'price', 'quantity')
    search_fields = ('product_name', 'order__order_id')


class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'subject', 'message')
    list_editable = ('status',)


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Enquiry, EnquiryAdmin)

