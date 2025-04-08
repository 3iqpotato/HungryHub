from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from myproject.suppliers.forms import SupplierForm
from myproject.suppliers.models import Supplier


# Create your views here.
@login_required
def complete_supplier_profile(request):
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
            return redirect('supplier_home_view')  # Или където искаш да пренасочиш след успешно запазване

    return render(request, 'supplier/complete_profile.html', {
        'form': form,
        'profile_type': 'Supplier'
    })


@login_required
def supplier_home_view(request):
    if request.method == 'GET':
        return render(request,'supplier/supplier_home.html', {"user": request.user})