from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, UpdateView

from myproject.orders.models import Cart
from myproject.restaurants.models import Restaurant
from myproject.users.forms import UserProfileForm
from myproject.users.models import UserProfile


# Create your views here.



@login_required
def complete_user_profile(request):
    if request.user.type != 'user':

        if request.user.type == 'supplier':
            return redirect('complete_supplier_profile')
        elif request.user.type == 'restaurant':
            return redirect('complete_restaurant_profile')
    # Проверяваме дали потребителят вече има профил
    try:
        profile = UserProfile.objects.get(account=request.user)
        # Ако има, използваме съществуващия (за редакция)
        form = UserProfileForm(request.POST or None, request.FILES or None, instance=profile)
    except UserProfile.DoesNotExist:
        # Ако няма, създаваме нов
        form = UserProfileForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            profile = form.save(commit=False)
            profile.account = request.user
            profile.save()
            return redirect('user_home', pk=profile.pk)

    return render(request, 'user/complete_user_profile.html', {
        'form': form,
        'profile_type': 'User'
    })


# @login_required
# def user_home_view(request):
#     if request.method == 'GET':
#         return render(request,'user/user_home.html', {"user": request.user})

UserModel = get_user_model()

def check_if_user_is_request_user(request, pk):
    profile = get_object_or_404(UserModel, pk=pk)
    return request.user == profile


class RegularUserHomeView(LoginRequiredMixin, DetailView, UserPassesTestMixin):
    model = UserProfile
    template_name = 'user/user_home.html'
    context_object_name = 'userprofile'
    pk_url_kwarg = 'pk'

    def test_func(self):
        """Проверява дали потребителят е собственикът на профила И е RegularUser"""
        user_profile = self.get_object()
        return (
            self.request.user == user_profile.user and  # Проверка дали е собственик
            self.request.user.type == 'user'  # Проверка дали е RegularUser
        )

    def dispatch(self, request, *args, **kwargs):
        # Проверка дали потребителят е логнат (LoginRequiredMixin)
        response = super().dispatch(request, *args, **kwargs)

        userprofile = self.get_object()
        if request.user != userprofile.account:
            raise PermissionDenied("Нямате достъп до този профил")

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавяне на допълнителен контекст ако е необходимо
        context['profile_type'] = 'RegularUser'
        context['restaurants'] = Restaurant.objects.all()
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'user/user_profile_edit.html'
    fields = ['name', 'img', 'phone_number', 'address'] # Пренасочва след успешно редактиране

    def get_object(self, queryset=None):
        # Връща профила на текущия потребител
        return self.request.user.userprofile

    def dispatch(self, request, *args, **kwargs):
        # Защита против опити за редактиране на чужд профил
        if self.kwargs.get('pk') != self.request.user.userprofile.pk:
            raise PermissionDenied("Нямате право да редактирате този профил")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        # Return URL string instead of redirect response
        return reverse('user_profile', kwargs={'pk': self.request.user.userprofile.pk})


class UserProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'user/user_profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        # Връща профила на текущия потребител
        profile = self.request.user.userprofile
        return profile

    def dispatch(self, request, *args, **kwargs):
        # Защита против опити за достъп до чужд профил чрез URL
        if self.kwargs.get('pk') != self.request.user.userprofile.pk:
            raise PermissionDenied("Нямате достъп до този профил")
        return super().dispatch(request, *args, **kwargs)


class UserCartDetailView(LoginRequiredMixin, DetailView):
    model = Cart
    template_name = 'user/user_cart.html'
    context_object_name = 'cart'

    def get_object(self):
            # Връща количката на текущия потребител
        cart, created = Cart.objects.get_or_create(user=self.request.user.userprofile)
        return cart

    def dispatch(self, request, *args, **kwargs):
            # Защита против опити за достъп до чужда количка
        if self.kwargs.get('pk') != request.user.userprofile.pk:
            raise PermissionDenied("Нямате достъп до тази количка")
        return super().dispatch(request, *args, **kwargs)