from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.complete_user_profile_api, name='api_complete_user_profile'),
    path('user_home/<int:pk>/', api_views.user_home_api, name='api_user_home'),
    path('user_cart/<int:pk>/', api_views.user_cart_api, name='api_user_cart'),
    path('user_profile/<int:pk>/', api_views.user_profile_api, name='api_user_profile'),
    path('user_profile/edit/<int:pk>/', api_views.edit_user_profile_api, name='api_edit_user_profile'),
    path('my-orders/', api_views.user_orders_api, name='api_user_orders'),
]