from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'price', 'rating', 'weight', 'category')
    list_filter = ('type', 'category')
    search_fields = ('name', 'ingredients')
    filter_horizontal = ('menus',)