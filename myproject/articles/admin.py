from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'price', 'rating', 'weight', 'menu')
    list_filter = ('type',)
    search_fields = ('name', 'ingredients')