from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from myproject.articles.models import Article


# Create your views here.
@login_required
@require_POST
def add_to_cart(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    cart = request.user.userprofile.cart

    # Проверка дали артикула е от различен ресторант
    if cart.items.exists():
        first_item_restaurant = cart.items.first().menu.restaurant
        if article.menu.restaurant != first_item_restaurant:
            # Изчистваме количката ако е от друг ресторант
            cart.items.clear()
            cart.total_price = 0
            cart.save()

    # Добавяне на артикула
    cart.items.add(article)
    cart.total_price = sum(item.price for item in cart.items.all())
    cart.save()

    return JsonResponse({
        'success': True,
        'cart_total': cart.total_price,
        'items_count': cart.items.count()
    })


@login_required
@require_POST
def remove_from_cart(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    cart = request.user.userprofile.cart

    if article in cart.items.all():
        cart.items.remove(article)
        # Преизчисляване на общата сума
        cart.total_price = sum(item.price for item in cart.items.all())
        cart.save()
        return JsonResponse({
            'success': True,
            'cart_total': cart.total_price,
            'items_count': cart.items.count()
        })
    return JsonResponse({'success': False}, status=400)