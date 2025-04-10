from django.contrib import admin

# Register your models here.
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('account', 'name', 'phone_number')
    search_fields = ('name', 'phone_number')
    raw_id_fields = ('account',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('account')