from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View

from myproject.orders.models import Order
from myproject.suppliers.forms import SupplierForm, SupplierProfileForm
from myproject.suppliers.models import Supplier


# Create your views here.
@login_required
def complete_supplier_profile(request):
    if request.user.type != 'supplier':
        if request.user.type == 'user':
            return redirect('complete_user_profile')
        elif request.user.type == 'restaurant':
            return redirect('complete_restaurant_profile')
    # Проверяваме дали вече има създаден профил
    try:
        supplier_profile = Supplier.objects.get(account=request.user)
        # Ако има, използваме съществуващия за редакция
        form = SupplierForm(request.POST or None, request.FILES or None, instance=supplier_profile)
    except Supplier.DoesNotExist:
        # Ако няма, създаваме нов формуляр
        form = SupplierForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.account = request.user
            supplier.save()
            return redirect('available_orders')  # Или където искаш да пренасочиш след успешно запазване

    return render(request, 'supplier/complete_supplier_profile.html', {
        'form': form,
        'profile_type': 'Supplier'
    })


class SupplierHomeView(LoginRequiredMixin, View):
    template_name = 'supplier/supplier_home.html'

    def dispatch(self, request, *args, **kwargs):
        # Проверка дали потребителят е доставчик
        if not hasattr(request.user, 'supplier'):
            raise PermissionDenied("Достъпът е разрешен само за доставчици")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        supplier = request.user.supplier
        active_orders = Order.objects.filter(
            supplier=supplier,
            status='on_delivery'
        ).count()

        delivered_orders = Order.objects.filter(
            supplier=supplier,
            status='delivered'
        ).count()

        context = {
            'supplier': supplier,
            'active_orders': active_orders,
            'delivered_orders': delivered_orders,
            'user': request.user
        }
        return render(request, self.template_name, context)


class SupplierAvailableOrdersView(LoginRequiredMixin, View):
    template_name = 'supplier/available_orders.html'

    def dispatch(self, request, *args, **kwargs):
        # Проверка дали потребителят е доставчик
        if not hasattr(request.user, 'supplier'):
            raise PermissionDenied("Достъпът е разрешен само за доставчици")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # Взимаме поръчките, които са готови за вземане
        available_orders = Order.objects.filter(
            status='ready_for_pickup'
        ).order_by('order_date_time')

        context = {
            'available_orders': available_orders,
            'current_time': timezone.now(),
        }
        return render(request, self.template_name, context)


class EditSupplierProfileView(LoginRequiredMixin, View):
    template_name = 'supplier/edit_profile.html'

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'supplier'):
            raise PermissionDenied("Достъпът е разрешен само за доставчици")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        supplier = request.user.supplier
        form = SupplierProfileForm(instance=supplier)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        supplier = request.user.supplier
        form = SupplierProfileForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_home_view')
        return render(request, self.template_name, {'form': form})