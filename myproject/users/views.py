from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

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
            return redirect('user_home')

    return render(request, 'user/complete_user_profile.html', {
        'form': form,
        'profile_type': 'User'
    })


@login_required
def user_home_view(request):
    if request.method == 'GET':
        return render(request,'user/user_home.html', {"user": request.user})
