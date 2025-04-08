from myproject.accounts import views
from django.urls import path

urlpatterns = [
    path('', views.register, name='register'),
]