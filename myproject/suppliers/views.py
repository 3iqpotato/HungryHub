from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
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
        print("jda")
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

        # Заплащане
        delivered_today = Order.objects.filter(
            supplier=supplier,
            status='delivered',
            delivery_time__date=timezone.now().date()
        )
        delivered_today_count = delivered_today.count()
        bonus = supplier.calculate_bonus()
        daily_earnings = delivered_today_count * 3 + bonus

        # Обороти
        daily_turnover = supplier.get_daily_turnover()
        monthly_turnover = supplier.get_monthly_turnover()

        active_orders = Order.objects.filter(supplier=supplier, status='on_delivery').count()
        delivered_orders = Order.objects.filter(supplier=supplier, status='delivered').count()

        context = {
            'supplier': supplier,
            'active_orders': active_orders,
            'delivered_orders': delivered_orders,
            'user': request.user,
            'daily_earnings': daily_earnings,
            'daily_turnover': daily_turnover,
            'monthly_turnover': monthly_turnover,
            'bonus': bonus,
            'delivered_today': delivered_today,  # Подаваме само доставените поръчки за днес
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



@login_required
def accept_order(request, order_id):
    # Проверка дали потребителят е доставчик
    if not hasattr(request.user, 'supplier'):
        return HttpResponseForbidden("Нямате права за това действие")

    # Взимане на поръчката
    order = get_object_or_404(Order, id=order_id)

    # Проверка дали поръчката е готова за вземане
    if order.status != 'ready_for_pickup':
        return HttpResponseForbidden("Поръчката не е налична за вземане")

    # Свързване на поръчката с доставчика
    order.status = 'on_delivery'
    order.supplier = request.user.supplier
    order.save()

    return redirect('supplier_active_orders')


@login_required
def supplier_active_orders(request):
    # Проверка дали потребителят е доставчик
    if not hasattr(request.user, 'supplier'):
        return HttpResponseForbidden("Нямате достъп до тази страница")

    # Взимаме активните поръчки на доставчика
    active_orders = Order.objects.filter(
        supplier=request.user.supplier,
        status='on_delivery'
    ).order_by('order_date_time')

    return render(request, 'supplier/active_orders.html', {
        'active_orders': active_orders
    })


@login_required
def mark_as_delivered(request, order_id):
    # Проверка дали потребителят е доставчик
    if not hasattr(request.user, 'supplier'):
        return HttpResponseForbidden("Нямате права за това действие")

    # Взимане на поръчката
    order = get_object_or_404(Order, id=order_id)

    # Проверка дали поръчката е на доставчика
    if order.supplier != request.user.supplier:
        return HttpResponseForbidden("Тази поръчка не е ваша")

    # Проверка на статуса
    if order.status != 'on_delivery':
        return HttpResponseForbidden("Невалидна операция")

    # Промяна на статуса
    order.status = 'delivered'
    order.save()

    return redirect('supplier_active_orders')


@login_required
def supplier_delivered_orders(request):
    # Проверка дали потребителят е доставчик
    if not hasattr(request.user, 'supplier'):
        return HttpResponseForbidden("Нямате достъп до тази страница")

    # Взимаме доставените поръчки на доставчика
    delivered_orders = Order.objects.filter(
        supplier=request.user.supplier,
        status='delivered'
    ).order_by('delivery_time')  # Най-новите първо

    return render(request, 'supplier/delivered_orders.html', {
        'delivered_orders': delivered_orders
    })