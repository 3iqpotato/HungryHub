from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, UpdateView

from myproject.articles.models import Article
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


class RestaurantHomeView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Restaurant
    template_name = 'restaurant/restaurant_home.html'
    context_object_name = 'restaurant'
    pk_url_kwarg = 'pk'

    def test_func(self):
        restaurant = self.get_object()
        return self.request.user == restaurant.account

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("Нямате достъп до този ресторант")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_type'] = 'Restaurant'
        return context


@login_required
def edit_restaurant(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)

    if request.user != restaurant.account:
        return redirect('restaurant_home_view', pk=restaurant.pk)

    if request.method == 'POST':
        restaurant.name = request.POST.get('name')
        restaurant.save()
        return redirect('restaurant_home_view', pk=restaurant.pk)

    return render(request, 'restaurant/edit_restaurant.html', {'restaurant': restaurant})



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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['articles'] = Article.objects.filter(menu=self.kwargs['pk'])
        return context

class MenuEditView(LoginRequiredMixin, UpdateView):
    model = Menu
    template_name = "restaurant/menu_edit.html"
    context_object_name = 'menu'
    pk_url_kwarg = 'pk'
    fields = ["name"]

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)


        menu = self.get_object()
        if request.user != menu.restaurant.account:
            raise PermissionDenied("Нямате достъп до това меню")

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['articles'] = Article.objects.filter(menu=self.kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        menu = self.get_object()
        if 'menu_name' in request.POST:  # Проверка за ръчната форма
            menu.name = request.POST['menu_name']
            menu.save()
        return super().post(request, *args, **kwargs)



class RestaurantMenuViewForUsers(LoginRequiredMixin, DetailView):
    model = Restaurant
    template_name = 'restaurant/restaurant_menu_for_users.html'
    pk_url_kwarg = 'pk'  # Взима ресторант по ID от URL

    def dispatch(self, request, *args, **kwargs):
        # Забраняваме достъп на ресторанти/доставчици
        if request.user.is_authenticated and request.user.type in ['restaurant', 'supplier']:
            raise PermissionDenied("Ресторанти и доставчици нямат достъп")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = self.get_object()

        # Взимаме менюто на ресторанта (1 към 1 връзка)
        menu = Menu.objects.get(restaurant=restaurant)

        # Взимаме артикулите от менюто (1 към много)
        articles = Article.objects.filter(menu=menu)

        # Добавяме всичко в контекста
        context.update({
            'restaurant': restaurant,
            'menu': menu,
            'articles': articles,
        })
        return context
