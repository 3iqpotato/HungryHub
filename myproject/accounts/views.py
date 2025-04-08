from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def index_view(request):
    return render(request, 'index.html')


from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import AccountRegistrationForm


def register(request):
    if request.method == 'POST':
        form = AccountRegistrationForm(request.POST)
        if form.is_valid():
            # Създаваме акаунт без username
            account = form.save(commit=False)
            account.username = form.cleaned_data['email']  # използваме email като username
            account.save()
            # Влизаме потребителя
            login(request, account)

            # Пренасочваме към допълнителната регистрация според типа
            if account.type == 'user':
                return redirect('complete_user_profile')
            elif account.type == 'supplier':
                return redirect('complete_supplier_profile')
            elif account.type == 'restaurant':
                return redirect('complete_restaurant_profile')
    else:
        form = AccountRegistrationForm()

    return render(request, 'register.html', {'form': form})




# @login_required
# def complete_supplier_profile(request):
#     if request.method == 'POST':
#         form = SupplierForm(request.POST, request.FILES)
#         if form.is_valid():
#             supplier = form.save(commit=False)
#             supplier.account = request.user
#             supplier.save()
#             return redirect('home')
#     else:
#         form = SupplierForm()
#
#     return render(request, 'accounts/complete_profile.html', {
#         'form': form,
#         'profile_type': 'Supplier'
#     })
#
#
# @login_required
# def complete_restaurant_profile(request):
#     if request.method == 'POST':
#         form = RestaurantForm(request.POST, request.FILES)
#         if form.is_valid():
#             restaurant = form.save(commit=False)
#             restaurant.account = request.user
#             restaurant.save()
#             return redirect('home')
#     else:
#         form = RestaurantForm()
#
#     return render(request, 'accounts/complete_profile.html', {
#         'form': form,
#         'profile_type': 'Restaurant'
#     })