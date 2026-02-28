from datetime import date
from decimal import Decimal

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from myproject.restaurants.models import Restaurant, Menu
from myproject.restaurants.serializers import RestaurantSerializer, RestaurantMiniSerializer, MenuSerializer
from myproject.articles.models import Article
from myproject.articles.serializers import ArticleSerializer
from myproject.orders.models import Order
from myproject.orders.serializers import OrderSerializer


def _ensure_restaurant_type(request):
    if request.user.type != "restaurant":
        return Response({"detail": "Този endpoint е само за restaurant"}, status=403)
    return None


def _ensure_restaurant_profile(request):
    if not hasattr(request.user, "restaurant"):
        return None, Response({"detail": "Нямате попълнен ресторант профил"}, status=403)
    return request.user.restaurant, None


def _ensure_own_restaurant(request, pk: int):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    if restaurant.account_id != request.user.id:
        raise PermissionDenied("Нямате достъп до този ресторант")
    return restaurant


def _get_or_create_menu_for_restaurant(restaurant: Restaurant):
    menu, _ = Menu.objects.get_or_create(restaurant=restaurant, defaults={"name": "NO name"})
    return menu


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def complete_restaurant_profile_api(request):
    """
    1:1 с complete_restaurant_profile:
    - GET: връща текущия профил (ако има) или празен
    - POST: create/update restaurant профил
    """
    bad = _ensure_restaurant_type(request)
    if bad:
        return bad

    restaurant = Restaurant.objects.filter(account=request.user).first()

    if request.method == "GET":
        if not restaurant:
            return Response({"profile_exists": False, "restaurant": None})
        return Response({"profile_exists": True, "restaurant": RestaurantSerializer(restaurant).data})

    # POST: create/update
    if restaurant:
        ser = RestaurantSerializer(restaurant, data=request.data, partial=True)
    else:
        ser = RestaurantSerializer(data=request.data)

    ser.is_valid(raise_exception=True)
    obj = ser.save(account=request.user)

    # меню по желание: да се гарантира, че има меню
    _get_or_create_menu_for_restaurant(obj)

    return Response({
        "status": "ok",
        "restaurant": RestaurantSerializer(obj).data,
        "next": "restaurant_home",
        "restaurant_id": obj.id
    }, status=status.HTTP_201_CREATED if not restaurant else 200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def restaurant_home_api(request, pk: int):
    """
    1:1 с RestaurantHomeView:
    - връща restaurant + daily/monthly turnover
    """
    bad = _ensure_restaurant_type(request)
    if bad:
        return bad

    restaurant = _ensure_own_restaurant(request, pk)

    today = date.today()

    orders_today = Order.objects.filter(restaurant=restaurant, order_date_time__date=today)
    daily_turnover = sum((o.total_price - o.delivery_fee) for o in orders_today)

    start_of_month = today.replace(day=1)
    orders_month = Order.objects.filter(restaurant=restaurant, order_date_time__date__gte=start_of_month)
    monthly_turnover = sum((o.total_price - o.delivery_fee) for o in orders_month)

    return Response({
        "restaurant": RestaurantSerializer(restaurant).data,
        "daily_turnover": str(daily_turnover),
        "monthly_turnover": str(monthly_turnover),
        "profile_type": "Restaurant"
    })


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def edit_restaurant_api(request, pk: int):
    """
    1:1 с edit_restaurant:
    - само owner може да редактира
    """
    bad = _ensure_restaurant_type(request)
    if bad:
        return bad

    restaurant = _ensure_own_restaurant(request, pk)

    partial = request.method == "PATCH"
    ser = RestaurantSerializer(restaurant, data=request.data, partial=partial)
    ser.is_valid(raise_exception=True)
    ser.save()

    return Response({
        "status": "ok",
        "restaurant": ser.data,
        "next": "restaurant_home",
        "restaurant_id": restaurant.id
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def menu_details_api(request, pk: int):
    """
    1:1 с MenuDetailsView:
    pk = restaurant_id (както при web ти: Menu.objects.get(restaurant=self.kwargs['pk']))
    """
    bad = _ensure_restaurant_type(request)
    if bad:
        return bad

    restaurant = _ensure_own_restaurant(request, pk)
    menu = _get_or_create_menu_for_restaurant(restaurant)

    # всички артикули в менюто
    articles = Article.objects.filter(menu=menu)

    return Response({
        "menu": MenuSerializer(menu).data,
        "articles": ArticleSerializer(articles, many=True).data
    })



@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def menu_edit_api(request, pk: int):
    bad = _ensure_restaurant_type(request)
    if bad:
        return bad

    restaurant = _ensure_own_restaurant(request, pk)
    menu = _get_or_create_menu_for_restaurant(restaurant)

    if request.method == "GET":
        articles = Article.objects.filter(menu=menu)
        return Response({
            "menu": MenuSerializer(menu).data,
            "articles": ArticleSerializer(articles, many=True).data
        })

    # PATCH
    ser = MenuSerializer(menu, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()

    articles = Article.objects.filter(menu=menu)
    return Response({
        "status": "ok",
        "menu": ser.data,
        "articles": ArticleSerializer(articles, many=True).data
    })

# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def menu_edit_api(request, pk: int):
#     """
#     GET /api/restaurants/restaurant/menu/<restaurant_id>/edit/
#     В web това е UpdateView + показва articles.
#     Тук GET връща menu + articles, а промяна на името ще правим с PATCH на същия endpoint.
#     """
#     bad = _ensure_restaurant_type(request)
#     if bad:
#         return bad
#
#     restaurant = _ensure_own_restaurant(request, pk)
#     menu = _get_or_create_menu_for_restaurant(restaurant)
#
#     if request.method == "GET":
#         articles = Article.objects.filter(menu=menu)
#         return Response({
#             "menu": MenuSerializer(menu).data,
#             "articles": ArticleSerializer(articles, many=True).data
#         })


# @api_view(["PATCH"])
# @permission_classes([IsAuthenticated])
# def menu_edit_api(request, pk: int):
#     """
#     PATCH /api/restaurants/restaurant/menu/<restaurant_id>/edit/
#     Body: { "name": "New menu name" }
#     """
#     bad = _ensure_restaurant_type(request)
#     if bad:
#         return bad
#
#     restaurant = _ensure_own_restaurant(request, pk)
#     menu = _get_or_create_menu_for_restaurant(restaurant)
#
#     ser = MenuSerializer(menu, data=request.data, partial=True)
#     ser.is_valid(raise_exception=True)
#     ser.save()
#
#     articles = Article.objects.filter(menu=menu)
#     return Response({
#         "status": "ok",
#         "menu": ser.data,
#         "articles": ArticleSerializer(articles, many=True).data
#     })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def menu_for_users_api(request, pk: int):
    """
    1:1 с RestaurantMenuViewForUsers:
    pk = restaurant_id
    Позволяваме само user (и guest ако махнеш IsAuthenticated).
    Може да филтрира по ?type=salads
    """
    if request.user.is_authenticated and request.user.type in ["restaurant", "supplier"]:
        return Response({"detail": "Ресторанти и доставчици нямат достъп"}, status=403)

    restaurant = get_object_or_404(Restaurant, pk=pk)
    menu = _get_or_create_menu_for_restaurant(restaurant)

    food_type = request.query_params.get("type")
    if food_type:
        articles = Article.objects.filter(menu=menu, type=food_type)
    else:
        articles = Article.objects.filter(menu=menu)

    return Response({
        "restaurant": RestaurantMiniSerializer(restaurant).data,
        "menu": MenuSerializer(menu).data,
        "articles": ArticleSerializer(articles, many=True).data,
        "selected_type": food_type
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def restaurant_orders_api(request):
    """
    1:1 с RestaurantOrdersView:
    връща поръчки по статус за текущия ресторант
    """
    bad = _ensure_restaurant_type(request)
    if bad:
        return bad

    restaurant, err = _ensure_restaurant_profile(request)
    if err:
        return err

    pending_orders = Order.objects.filter(restaurant=restaurant, status="pending").order_by("order_date_time")
    ready_orders = Order.objects.filter(restaurant=restaurant, status="ready_for_pickup").order_by("order_date_time")
    delivered_orders = Order.objects.filter(restaurant=restaurant, status__in=["delivered", "on_delivery"]).order_by("order_date_time")

    return Response({
        "restaurant": RestaurantMiniSerializer(restaurant).data,
        "pending_orders": OrderSerializer(pending_orders, many=True).data,
        "ready_orders": OrderSerializer(ready_orders, many=True).data,
        "delivered_orders": OrderSerializer(delivered_orders, many=True).data,
    })