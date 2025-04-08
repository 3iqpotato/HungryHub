from django.urls import path

from myproject.suppliers import views

urlpatterns = [
    path('', views.complete_supplier_profile, name='complete_supplier_profile'),
    path('supplier_home/', views.supplier_home_view, name='supplier_home_view'),
]