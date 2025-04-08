from myproject.accounts import views
from django.urls import path

from myproject.accounts.views import CustomLoginView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('complete-profile-redirect/', views.complete_profile_redirect, name='complete_profile_redirect'),
]