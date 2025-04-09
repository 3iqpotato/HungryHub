from myproject.accounts import views
from django.urls import path

from myproject.accounts.views import CustomLoginView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.home_view, name='home_view'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('complete-profile-redirect/', views.complete_profile_redirect, name='complete_profile_redirect'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
]