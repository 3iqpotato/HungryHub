from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.complete_restaurant_profile_api, name='api_complete_restaurant_profile'),
    path('restaurant_home/<int:pk>/', api_views.restaurant_home_api, name='api_restaurant_home'),
    path('restaurant/<int:pk>/edit/', api_views.edit_restaurant_api, name='api_edit_restaurant'),
    path('restaurant/menu/<int:pk>/', api_views.menu_details_api, name='api_menu_details'),
    path('restaurant/menu_for_users/<int:pk>/', api_views.menu_for_users_api, name='api_menu_for_users'),
    path('restaurant/menu/<int:pk>/edit/', api_views.menu_edit_api, name='api_menu_edit'),
    path('restaurant/orders/', api_views.restaurant_orders_api, name='api_restaurant_orders'),
]