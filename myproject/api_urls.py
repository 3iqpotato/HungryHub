from django.urls import path, include

urlpatterns = [
    path("accounts/", include("myproject.accounts.api_urls")),
    path("users/", include("myproject.users.api_urls")),
    path("suppliers/", include("myproject.suppliers.api_urls")),
    path("restaurants/", include("myproject.restaurants.api_urls")),
    path("articles/", include("myproject.articles.api_urls")),
    path("orders/", include("myproject.orders.api_urls")),
]