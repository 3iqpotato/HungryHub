from django.urls import path

from myproject.users import views

urlpatterns = [
    path('', views.complete_user_profile, name='complete_user_profile'),
    path('user_home/<int:pk>', views.RegularUserHomeView.as_view(), name='user_home'),
    path('user_profile/<int:pk>', views.UserProfileView.as_view(), name='user_profile'),
    path('user_profile/edit/<int:pk>', views.EditProfileView.as_view(), name='user_profile_edit'),
]