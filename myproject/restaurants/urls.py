from django.urls import path

from myproject.restaurants import views

urlpatterns = [
    path('', views.complete_restaurant_profile, name='complete_restaurant_profile'),
    path('restaurant_home/', views.restaurant_home_view, name='restaurant_home_view'),
]