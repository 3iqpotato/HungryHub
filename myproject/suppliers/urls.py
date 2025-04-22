from django.urls import path

from myproject.suppliers import views
from myproject.suppliers.views import SupplierAvailableOrdersView, EditSupplierProfileView, accept_order, \
    supplier_active_orders, mark_as_delivered, supplier_delivered_orders

urlpatterns = [
    path('', views.complete_supplier_profile, name='complete_supplier_profile'),
    path('supplier_home/', views.SupplierHomeView.as_view(), name='supplier_home_view'),
    path('supplier/available-orders/', SupplierAvailableOrdersView.as_view(), name='available_orders'),
    path('supplier/edit-profile/', EditSupplierProfileView.as_view(), name='edit_supplier_profile'),
    path('supplier/accept_order/<int:order_id>', accept_order, name='accept_order'),
    path('supplier/active-orders/', supplier_active_orders, name='supplier_active_orders'),
    path('supplier/mark-delivered/<int:order_id>/', mark_as_delivered, name='mark_delivered'),
    path('supplier/delivered-orders/', supplier_delivered_orders, name='supplier_delivered_orders'),
]