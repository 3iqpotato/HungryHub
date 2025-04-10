from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView

from myproject.restaurants.forms import RestaurantForm, RestaurantEditForm
from myproject.restaurants.models import Restaurant, Menu


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
            return redirect('restaurant_home_view', pk=restaurant.pk)  # Пренасочване след успешно запазване

    return render(request, 'restaurant/complete_restaurant_profile.html', {
        'form': form,
        'profile_type': 'Restaurant',
        'is_update': is_update  # Подаваме флаг дали е редакция
    })



UserModel = get_user_model()

def check_if_user_is_request_user(request, pk):
    profile = get_object_or_404(UserModel, pk=pk)
    return request.user == profile


class RestaurantHomeView(LoginRequiredMixin, DetailView, UserPassesTestMixin):
    model = Restaurant
    template_name = 'restaurant/restaurant_home.html'
    context_object_name = 'restaurant'
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        # Проверка дали потребителят е логнат (LoginRequiredMixin)
        response = super().dispatch(request, *args, **kwargs)

        restaurant = self.get_object()
        if request.user != restaurant.account:
            raise PermissionDenied("Нямате достъп до този ресторант")

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавяне на допълнителен контекст ако е необходимо
        context['profile_type'] = 'Restaurant'
        return context


@login_required
def edit_restaurant(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)

    # Проверка дали потребителят е собственик на ресторанта
    if request.user != restaurant.account:
        return redirect('restaurant_home_view', pk=restaurant.pk)

    if request.method == 'POST':
        form = RestaurantEditForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            return redirect('restaurant_home_view', pk=restaurant.pk)
    else:
        form = RestaurantEditForm(instance=restaurant)

    return render(request, 'restaurant/edit_restaurant.html', {
        'form': form,
        'restaurant': restaurant
    })

class MenuDetailsView(LoginRequiredMixin, DetailView):
    model = Menu
    template_name = "restaurant/menu_details.html"
    context_object_name = 'menu'
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        # Проверка дали потребителят е логнат (LoginRequiredMixin)
        response = super().dispatch(request, *args, **kwargs)


        menu = self.get_object()
        if request.user != menu.restaurant.account:
            raise PermissionDenied("Нямате достъп до това меню")

        return response

    def get_object(self, queryset=None):
        return Menu.objects.get(restaurant=self.kwargs['pk'])