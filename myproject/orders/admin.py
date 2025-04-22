from django.contrib import admin
from .models import Cart, Order

from django.contrib import admin
from .models import Cart, Order, CartItem


# Админ панел за Cart
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_total_price')

    # Добавяме метод за показване на общата сума
    def get_total_price(self, obj):
        return sum(item.get_total_price() for item in obj.items.all())

    get_total_price.short_description = 'Total Price'


# Админ панел за Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'user', 'supplier', 'restaurant', 'get_total_price')
    list_filter = ('status',)
    raw_id_fields = ('user', 'supplier', 'restaurant')
    date_hierarchy = 'order_date_time'

    # Добавяме метод за показване на общата сума на поръчката
    def get_total_price(self, obj):
        return sum(item.get_total_price() for item in obj.items.all())

    get_total_price.short_description = 'Total Price'


# Админ панел за CartItem (ако е необходимо)
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'article', 'quantity', 'get_total_price')

    # Преобразуваме цена
    def get_total_price(self, obj):
        return obj.get_total_price()

    get_total_price.short_description = 'Total Price'
