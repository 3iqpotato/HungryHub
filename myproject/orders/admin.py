from django.contrib import admin
from .models import Cart, Order

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'price')
    filter_horizontal = ('items',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'price', 'user', 'supplier', 'restaurant')
    list_filter = ('status',)
    raw_id_fields = ('user', 'cart', 'supplier', 'restaurant')
    date_hierarchy = 'order_date_time'