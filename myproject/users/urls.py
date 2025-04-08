from django.urls import path

from myproject.users import views

urlpatterns = [
    path('', views.complete_user_profile, name='complete_user_profile'),
    path('user_home/', views.user_home_view, name='user_home'),
]