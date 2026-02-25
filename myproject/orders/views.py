from decimal import Decimal
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
        if not hasattr(request.user, 'userprofile'):
            return HttpResponseBadRequest("Не сте влезли в системата")

        user_profile = request.user.userprofile

        if not user_profile.cart.items.exists():
            return HttpResponseBadRequest("Количката ви е празна")

        cart_items = user_profile.cart.items.select_related(
            'article__menu__restaurant'
        ).all()

        restaurant = None
        for item in cart_items:
            if not restaurant:
                restaurant = item.article.menu.restaurant
            elif item.article.menu.restaurant != restaurant:
                return HttpResponseBadRequest("Не можете да поръчвате от множество ресторанти наведнъж")

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=user_profile,
                    restaurant=restaurant,
                    status='pending',
                    address_for_delivery=user_profile.address,
                    order_date_time=timezone.now(),
                    delivery_time=timezone.now() + timezone.timedelta(minutes=45)
                )

                # 1) правим OrderItems + смятаме subtotal от КОЛИЧКАТА (най-сигурно)
                order_items = []
                subtotal = Decimal("0.00")

                for cart_item in cart_items:
                    price = Decimal(str(cart_item.article.price))
                    qty = Decimal(str(cart_item.quantity))
                    subtotal += price * qty

                    order_items.append(OrderItem(
                        order=order,
                        article=cart_item.article,
                        quantity=cart_item.quantity,
                        # ако имаш поле price_at_purchase -> запиши price тук
                    ))

                OrderItem.objects.bulk_create(order_items)

                # 2) смятаме таксата 3 лв при subtotal < 30
                delivery_fee = Decimal("3.00") if (subtotal > 0 and subtotal < Decimal("30.00")) else Decimal("0.00")

                # 3) записваме в order (заключваме стойностите)
                order.delivery_fee = delivery_fee
                order.total_price = subtotal + delivery_fee
                order.save(update_fields=["delivery_fee", "total_price"])

                # 4) чистим количката
                cart_items.delete()

        except Exception as e:
            print(f"Грешка при създаване на поръчка: {str(e)}")
            return HttpResponseBadRequest("Възникна грешка при обработката на поръчката")

        return HttpResponseRedirect(reverse('order_detail', args=[order.id]) + "?success=1")

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