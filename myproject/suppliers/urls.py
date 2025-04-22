from django.urls import path

from myproject.suppliers import views
from myproject.suppliers.views import SupplierAvailableOrdersView, EditSupplierProfileView

urlpatterns = [
    path('', views.complete_supplier_profile, name='complete_supplier_profile'),
    path('supplier_home/', views.SupplierHomeView.as_view(), name='supplier_home_view'),
    path('supplier/available-orders/', SupplierAvailableOrdersView.as_view(), name='available_orders'),
    path('supplier/edit-profile/', EditSupplierProfileView.as_view(), name='edit_supplier_profile'),
]