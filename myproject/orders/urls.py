from django.urls import path

from . import views
from .views import add_to_cart, remove_from_cart, CreateOrderView, MarkOrderReadyView

urlpatterns = [
    path('add-to-cart/<int:article_id>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<int:article_id>/', remove_from_cart, name='remove-from-cart'),
    path('orders/create_order/', CreateOrderView.as_view(), name='create_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/ready/', MarkOrderReadyView.as_view(), name='mark_order_ready'),
]