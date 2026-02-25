from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('account', 'name', 'phone_number', 'type')
    list_filter = ('type',)
    search_fields = ('name', 'phone_number')
    raw_id_fields = ('account',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('account')