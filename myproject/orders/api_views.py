from decimal import Decimal

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from myproject.articles.models import Article
from myproject.orders.models import Cart, CartItem, Order, OrderItem
from myproject.orders.serializers import CartSerializer, OrderSerializer


def _require_user_profile(request):
    if not hasattr(request.user, "userprofile"):
        return None, Response({"detail": "Нямате user профил"}, status=403)
    return request.user.userprofile, None


def _ensure_cart(profile):
    cart, _ = Cart.objects.get_or_create(user=profile)
    return cart


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart_api(request, article_id: int):
    """
    POST /api/orders/add-to-cart/<article_id>/
    Прави същото като add_to_cart:
    - ако има артикули от друг ресторант -> чисти количката
    - ако артикулът вече е там -> quantity++
    Връща cart totals + items.
    """
    profile, err = _require_user_profile(request)
    if err:
        return err

    if request.user.type != "user":
        return Response({"detail": "Само потребител може да добавя в количка"}, status=403)

    article = get_object_or_404(Article, id=article_id)
    cart = _ensure_cart(profile)

    # ако количката има items, и ресторантът е различен -> чистим количката
    if cart.items.exists():
        first_item = cart.items.select_related("article__menu__restaurant").first()
        first_restaurant = first_item.article.menu.restaurant
        current_restaurant = article.menu.restaurant
        if current_restaurant != first_restaurant:
            cart.items.all().delete()

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        article=article,
        defaults={"quantity": 1},
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save(update_fields=["quantity"])

    # връщаме цялата количка (по-добре от само totals)
    return Response({
        "success": True,
        "cart": CartSerializer(cart).data
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_from_cart_api(request, article_id: int):
    """
    POST /api/orders/remove-from-cart/<article_id>/
    В твоя web код параметърът е id на CartItem (не Article).
    Запазвам същото: тук article_id всъщност е cart_item_id.
    """
    profile, err = _require_user_profile(request)
    if err:
        return err

    if request.user.type != "user":
        return Response({"detail": "Само потребител може да маха от количка"}, status=403)

    cart = _ensure_cart(profile)

    cart_item = get_object_or_404(CartItem, id=article_id)
    if cart_item.cart_id != cart.id:
        return Response({"success": False, "error": "Item not in cart"}, status=400)

    cart_item.delete()

    return Response({
        "success": True,
        "cart": CartSerializer(cart).data
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order_api(request):
    """
    POST /api/orders/orders/create_order/
    1:1 с CreateOrderView.post:
    - иска userprofile
    - profile must be complete
    - cart not empty
    - само 1 ресторант
    - прави Order + OrderItems
    - delivery_fee: 3 лв ако subtotal < 30
    - чисти cart
    Връща order + next.
    """
    profile, err = _require_user_profile(request)
    if err:
        return err

    if request.user.type != "user":
        return Response({"detail": "Само потребител може да прави поръчка"}, status=403)

    if not profile.is_complete():
        return Response({
            "error": "profile_incomplete",
            "message": "Моля, попълнете адрес и телефон преди да направите поръчка.",
            "next": "complete_user_profile"
        }, status=400)

    cart = _ensure_cart(profile)

    if not cart.items.exists():
        return Response({"detail": "Количката ви е празна"}, status=400)

    cart_items = cart.items.select_related("article__menu__restaurant").all()

    restaurant = None
    for item in cart_items:
        if not restaurant:
            restaurant = item.article.menu.restaurant
        elif item.article.menu.restaurant != restaurant:
            return Response({"detail": "Не можете да поръчвате от множество ресторанти наведнъж"}, status=400)

    try:
        with transaction.atomic():
            order = Order.objects.create(
                user=profile,
                restaurant=restaurant,
                status="pending",
                address_for_delivery=profile.address,
                order_date_time=timezone.now(),
                delivery_time=timezone.now() + timezone.timedelta(minutes=45),
            )

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
                ))

            OrderItem.objects.bulk_create(order_items)

            delivery_fee = Decimal("3.00") if (subtotal > 0 and subtotal < Decimal("30.00")) else Decimal("0.00")

            order.delivery_fee = delivery_fee
            order.total_price = subtotal + delivery_fee
            order.save(update_fields=["delivery_fee", "total_price"])

            cart_items.delete()

    except Exception as e:
        return Response({"detail": f"Възникна грешка при обработката на поръчката: {str(e)}"}, status=400)

    return Response({
        "status": "ok",
        "order": OrderSerializer(order).data,
        "next": "order_detail",
        "order_id": order.id
    }, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_detail_api(request, order_id: int):
    """
    GET /api/orders/order/<order_id>/
    1:1 с order_detail:
    - user вижда само свои
    - restaurant вижда само свои
    - supplier: засега allow (по твоя TODO)
    Връща order JSON + flags can_update/can_pickup.
    """
    order = get_object_or_404(Order, id=order_id)

    user = request.user

    if user.type == "user":
        if not hasattr(user, "userprofile") or order.user_id != user.userprofile.id:
            return Response({"error": "Unauthorized"}, status=403)

    elif user.type == "restaurant":
        if not hasattr(user, "restaurant") or order.restaurant_id != user.restaurant.id:
            return Response({"error": "Unauthorized"}, status=403)

    elif user.type == "supplier":
        # TODO: ако искаш, тук ще добавим правила кой доставчик вижда коя поръчка
        pass

    # flags за UI (ако ти трябват в MAUI)
    can_update = (user.type == "restaurant" and hasattr(user, "restaurant") and user.restaurant == order.restaurant and order.status != "ready_for_pickup")
    can_pickup = (order.status == "ready_for_pickup" and user.type == "supplier")

    return Response({
        "order": OrderSerializer(order).data,
        "can_update": can_update,
        "can_pickup": can_pickup,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_order_ready_api(request, order_id: int):
    """
    POST /api/orders/order/<order_id>/ready/
    1:1 с MarkOrderReadyView.post:
    - само restaurant owner може да маркира ready_for_pickup
    """
    order = get_object_or_404(Order, pk=order_id)

    if request.user.type != "restaurant" or not hasattr(request.user, "restaurant") or request.user.restaurant != order.restaurant:
        return Response({"detail": "Нямате право да променяте тази поръчка"}, status=403)

    order.status = "ready_for_pickup"
    # ти имаш order.status_updated_at в view-а, но в модела не го виждам.
    # ако нямаш такова поле -> махни следващия ред.
    if hasattr(order, "status_updated_at"):
        order.status_updated_at = timezone.now()

    order.save()

    return Response({
        "status": "ok",
        "order": OrderSerializer(order).data
    })