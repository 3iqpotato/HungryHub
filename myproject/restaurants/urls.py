from django.urls import path

from myproject.restaurants import views
from myproject.restaurants.views import RestaurantOrdersView

urlpatterns = [
    path('', views.complete_restaurant_profile, name='complete_restaurant_profile'),
    path('restaurant_home/<int:pk>', views.RestaurantHomeView.as_view(), name='restaurant_home_view'),
    path('restaurant/<int:pk>/edit/', views.edit_restaurant, name='edit_restaurant'),
    path('restaurant/menu/<int:pk>/', views.MenuDetailsView.as_view(), name='restaurant_menu'),
    path('restaurant/menu_for_users/<int:pk>/', views.RestaurantMenuViewForUsers.as_view(), name='restaurant_menu_for_users'),
    path('restaurant/menu/<int:pk>/edit/', views.MenuEditView.as_view(), name='restaurant_menu_edit'),
    path('restaurant/orders/', RestaurantOrdersView.as_view(), name='restaurant_orders'),
]