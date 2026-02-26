from django.urls import path
from . import api_views

urlpatterns = [
    path("register/", api_views.register_api, name="api_register"),
    path("login/", api_views.login_api, name="api_login"),
    path("logout/", api_views.logout_api, name="api_logout"),
]