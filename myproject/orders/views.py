from pprint import pprint

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.checks import messages
from django.http import JsonResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_POST

from myproject.articles.models import Article
from myproject.orders.models import Order, CartItem, OrderItem


# Create your views here.
@login_required
@require_POST
def add_to_cart(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    cart = request.user.userprofile.cart

    # Проверка дали има артикули в количката
    if cart.items.exists():
        first_item = cart.items.first()
        first_restaurant = first_item.article.menu.restaurant
        current_restaurant = article.menu.restaurant

        if current_restaurant != first_restaurant:
            # Изтриваме всички CartItem обекти от количката
            cart.items.all().delete()

    # Търсим дали вече има такъв артикул в количката
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        article=article,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Изчисляване на общата стойност
    total_price = sum(item.get_total_price() for item in cart.items.all())
    items_count = sum(item.quantity for item in cart.items.all())

    return JsonResponse({
        'success': True,
        'cart_total': float(total_price),
        'items_count': items_count
    })


@login_required
@require_POST
def remove_from_cart(request, article_id):
    cart_item = get_object_or_404(CartItem, id=article_id)
    cart = request.user.userprofile.cart

    # Търсим CartItem, свързан с този артикул и тази количка
    try:
        cart_item = CartItem.objects.get(cart=cart, id=cart_item.id)
        cart_item.delete()
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not in cart'}, status=400)

    # Преизчисляване на общата стойност
    total_price = sum(item.article.price * item.quantity for item in cart.items.all())

    return JsonResponse({
        'success': True,
        'cart_total': total_price,
        'items_count': cart.items.count()
    })


from django.views import View
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.db import transaction
from .models import Order, OrderItem, CartItem


class CreateOrderView(View):
    def post(self, request):
        # Проверка дали потребителят е логнат и има UserProfile
        if not hasattr(request.user, 'userprofile'):
            return HttpResponseBadRequest("Не сте влезли в системата")

        user_profile = request.user.userprofile

        # Проверка за количка
        if not user_profile.cart.items.exists():
            return HttpResponseBadRequest("Количката ви е празна")

        # Взимане на всички артикули от количката
        cart_items = user_profile.cart.items.select_related(
            'article__menu__restaurant'
        ).all()

        # Проверка за ресторанти
        restaurant = None
        for item in cart_items:
            if not restaurant:
                restaurant = item.article.menu.restaurant
            elif item.article.menu.restaurant != restaurant:
                return HttpResponseBadRequest(
                    "Не можете да поръчвате от множество ресторанти наведнъж"
                )

        # Създаване на поръчка в transaction за сигурност
        try:
            with transaction.atomic():
                # Създаване на поръчка
                order = Order.objects.create(
                    user=user_profile,
                    restaurant=restaurant,
                    status='pending',
                    address_for_delivery=user_profile.address,
                    order_date_time=timezone.now(),
                    delivery_time=timezone.now() + timezone.timedelta(minutes=45)  # Примерно време за доставка
                )

                # Създаване на OrderItems от CartItems
                order_items = []
                for cart_item in cart_items:
                    order_items.append(OrderItem(
                        order=order,
                        article=cart_item.article,
                        quantity=cart_item.quantity, # Запазване на цената към момента на поръчката
                    ))

                OrderItem.objects.bulk_create(order_items)

                # Изтриване на артикулите от количката
                cart_items.delete()

                # Опционално: изчисляване на общата сума и запазването й в поръчката
                order.total_price = sum(
                    item.article.price * item.quantity
                    for item in order.order_items.all()
                ) + (restaurant.delivery_fee if restaurant.delivery_fee else 0)
                order.save()

        except Exception as e:
            # Логване на грешката
            print(f"Грешка при създаване на поръчка: {str(e)}")
            return HttpResponseBadRequest("Възникна грешка при обработката на поръчката")

        # Пренасочване към детайлите на поръчката
        return HttpResponseRedirect(
            reverse('order_detail', args=[order.id]) + "?success=1"
        )


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    user = request.user
    if user.type == 'user':
        if order.user != request.user.userprofile:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

    elif user.type == 'supplier':

        pass #TODO

    elif user.type == 'restaurant':
        if order.restaurant != request.user.restaurant:
            return JsonResponse({'error': 'Unauthorized'}, status=403)


    # Проверка дали ресторантът може да промени статуса на поръчката
    can_update = request.user == order.restaurant and order.status != 'ready_for_pickup'

    # Проверка дали доставчик може да вземе поръчката
    can_pickup = order.status == 'ready_for_pickup' and request.user.type == 'supplier'

    context = {
        'order': order,
        'can_update': can_update,
        'can_pickup': can_pickup,
    }
    return render(request, 'order/order_details.html', context)


class MarkOrderReadyView(LoginRequiredMixin, View):
    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)

        # Проверка дали потребителят е от ресторанта
        if not hasattr(request.user, 'restaurant') or \
                request.user.restaurant != order.restaurant:
            return redirect('restaurant_orders')

        # Промяна на статуса
        order.status = 'ready_for_pickup'
        order.status_updated_at = timezone.now()
        order.save()

        return redirect('restaurant_orders')