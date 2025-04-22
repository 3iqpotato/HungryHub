from django.urls import path
from .views import add_to_cart, remove_from_cart

urlpatterns = [
    path('add-to-cart/<int:article_id>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<int:article_id>/', remove_from_cart, name='remove-from-cart'),
]