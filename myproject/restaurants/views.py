from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from myproject.restaurants.forms import RestaurantForm
from myproject.restaurants.models import Restaurant


# Create your views here.
@login_required
def complete_restaurant_profile(request):
    if request.user.type != 'restaurant':
        if request.user.type == 'user':
            return redirect('complete_user_profile')
        if request.user.type == 'supplier':
            return redirect('complete_supplier_profile')

    # Проверяваме дали вече съществува профил за ресторанта
    try:
        restaurant_profile = Restaurant.objects.get(account=request.user)
        # Ако има, използваме съществуващия за редакция
        form = RestaurantForm(request.POST or None, request.FILES or None, instance=restaurant_profile)
        is_update = True
    except Restaurant.DoesNotExist:
        # Ако няма, създаваме нов формуляр
        form = RestaurantForm(request.POST or None, request.FILES or None)
        is_update = False

    if request.method == 'POST':
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.account = request.user
            restaurant.save()
            return redirect('restaurant_home_view')  # Пренасочване след успешно запазване

    return render(request, 'restaurant/complete_profile.html', {
        'form': form,
        'profile_type': 'Restaurant',
        'is_update': is_update  # Подаваме флаг дали е редакция
    })


@login_required
def restaurant_home_view(request):
    if request.method == 'GET':
        return render(request,'restaurant/restaurant_home.html', {"user": request.user})