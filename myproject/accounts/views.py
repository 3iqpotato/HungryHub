from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse


def index_view(request):
    return render(request, 'index.html')


from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import AccountRegistrationForm, LoginForm


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


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'

    def get_success_url(self):
        # Пренасочване според типа потребител след успешен логин
        user = self.request.user
        if user.type == 'user' and hasattr(user, 'userprofile'):
            return reverse('user_home')
        elif user.type == 'supplier' and hasattr(user, 'supplier'):
            return reverse('supplier_home_view')
        elif user.type == 'restaurant' and hasattr(user, 'restaurant'):
            return reverse('restaurant_home_view')
        # Ако няма попълнен профил, пренасочи към попълване
        return reverse('complete_profile_redirect')


def complete_profile_redirect(request):
    user = request.user
    if user.type == 'user':
        return redirect('complete_user_profile')
    elif user.type == 'supplier':
        return redirect('complete_supplier_profile')
    elif user.type == 'restaurant':
        return redirect('complete_restaurant_profile')


def home_view(request):
    return render(request, 'index.html')


class CustomLogoutView(LogoutView):
    next_page = 'home_view'  # Страница за пренасочване след изход