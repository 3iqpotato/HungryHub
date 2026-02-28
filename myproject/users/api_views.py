from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.core.exceptions import PermissionDenied

from myproject.users.models import UserProfile
from myproject.users.serializers import UserProfileSerializer

from myproject.orders.models import Cart, Order
from myproject.orders.serializers import CartSerializer, OrderSerializer

from myproject.restaurants.models import Restaurant
from myproject.restaurants.serializers import RestaurantMiniSerializer


def _ensure_user_type(request):
    if request.user.type != "user":
        return Response({"detail": "Този endpoint е само за тип user"}, status=403)
    return None


def _ensure_own_profile(request, pk: int):
    if not hasattr(request.user, "userprofile"):
        raise PermissionDenied("Нямате профил")
    if request.user.userprofile.pk != pk:
        raise PermissionDenied("Нямате достъп до този профил")


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def complete_user_profile_api(request):
    """
    1:1 с complete_user_profile:
    - GET: връща текущия профил
    - POST: попълва/редактира профила (partial update)
    """
    bad = _ensure_user_type(request)
    if bad:
        return bad

    profile, _ = UserProfile.objects.get_or_create(account=request.user)

    if request.method == "GET":
        return Response(UserProfileSerializer(profile).data)

    ser = UserProfileSerializer(profile, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()

    if profile.is_complete():
        return Response({
            "status": "ok",
            "profile": UserProfileSerializer(profile).data,
            "next": "user_home",
            "profile_id": profile.id,
        })

    return Response({
        "status": "ok",
        "profile": UserProfileSerializer(profile).data,
        "next": "complete_user_profile",
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_home_api(request, pk: int):
    bad = _ensure_user_type(request)
    if bad:
        return bad

    _ensure_own_profile(request, pk)

    profile = request.user.userprofile
    restaurants = Restaurant.objects.all()

    return Response({
        "profile": UserProfileSerializer(profile).data,
        "restaurants": RestaurantMiniSerializer(restaurants, many=True).data
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile_api(request, pk: int):
    bad = _ensure_user_type(request)
    if bad:
        return bad

    _ensure_own_profile(request, pk)
    return Response(UserProfileSerializer(request.user.userprofile).data)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def edit_user_profile_api(request, pk: int):
    bad = _ensure_user_type(request)
    if bad:
        return bad

    _ensure_own_profile(request, pk)

    profile = request.user.userprofile
    partial = request.method == "PATCH"

    ser = UserProfileSerializer(profile, data=request.data, partial=partial)
    ser.is_valid(raise_exception=True)
    ser.save()

    return Response({
        "status": "ok",
        "profile": ser.data
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_cart_api(request, pk: int):
    bad = _ensure_user_type(request)
    if bad:
        return bad

    _ensure_own_profile(request, pk)

    profile = request.user.userprofile
    cart, _ = Cart.objects.get_or_create(user=profile)

    return Response({
        "user_profile_id": profile.id,
        "cart": CartSerializer(cart).data
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_orders_api(request):
    bad = _ensure_user_type(request)
    if bad:
        return bad

    if not hasattr(request.user, "userprofile"):
        return Response({"detail": "Нямате профил"}, status=400)

    orders = Order.objects.filter(user=request.user.userprofile).order_by("-order_date_time")
    return Response(OrderSerializer(orders, many=True).data)