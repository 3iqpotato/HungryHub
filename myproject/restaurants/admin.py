from django.contrib import admin
from .models import Restaurant, Menu


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('account', 'name', 'phone_number', 'rating', 'discount')
    search_fields = ('name', 'phone_number', 'address')
    raw_id_fields = ('account',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('account')


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant')
    raw_id_fields = ('restaurant',)