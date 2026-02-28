from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.utils import timezone

from myproject.orders.models import Order
from myproject.orders.serializers import OrderSerializer
from myproject.suppliers.models import Supplier
from myproject.suppliers.serializers import SupplierSerializer


def _ensure_supplier_type(request):
    if request.user.type != "supplier":
        return Response({"detail": "Този endpoint е само за supplier"}, status=403)
    return None


def _ensure_supplier_profile(request):
    if not hasattr(request.user, "supplier"):
        return None, Response({"detail": "Нямате попълнен supplier профил"}, status=403)
    return request.user.supplier, None


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def complete_supplier_profile_api(request):
    """
    1:1 с complete_supplier_profile:
    - GET: връща профила ако има
    - POST: create/update профил
    """
    bad = _ensure_supplier_type(request)
    if bad:
        return bad

    supplier = Supplier.objects.filter(account=request.user).first()

    if request.method == "GET":
        if not supplier:
            return Response({"profile_exists": False, "supplier": None})
        return Response({"profile_exists": True, "supplier": SupplierSerializer(supplier).data})

    # POST create/update
    if supplier:
        ser = SupplierSerializer(supplier, data=request.data, partial=True)
    else:
        ser = SupplierSerializer(data=request.data)

    ser.is_valid(raise_exception=True)
    obj = ser.save(account=request.user)

    return Response({
        "status": "ok",
        "supplier": SupplierSerializer(obj).data,
        "next": "available_orders"
    }, status=status.HTTP_201_CREATED if not supplier else 200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def supplier_home_api(request):
    """
    1:1 с SupplierHomeView.get:
    връща:
    - supplier
    - active_orders count
    - delivered_orders count
    - delivered_today_count
    - daily_earnings
    - month_earnings
    """
    bad = _ensure_supplier_type(request)
    if bad:
        return bad

    supplier, err = _ensure_supplier_profile(request)
    if err:
        return err

    today = timezone.now().date()

    delivered_today_qs = Order.objects.filter(
        supplier=supplier,
        status="delivered",
        delivery_time__date=today
    )
    delivered_today_count = delivered_today_qs.count()

    daily_earnings = supplier.get_daily_earnings()
    month_earnings = supplier.get_monthly_earnings()

    active_orders_count = Order.objects.filter(supplier=supplier, status="on_delivery").count()
    delivered_orders_count = Order.objects.filter(supplier=supplier, status="delivered").count()

    return Response({
        "supplier": SupplierSerializer(supplier).data,
        "active_orders": active_orders_count,
        "delivered_orders": delivered_orders_count,
        "delivered_today_count": delivered_today_count,
        "daily_earnings": str(daily_earnings),
        "month_earnings": str(month_earnings),
        # ако искаш да покажеш списък с доставени днес:
        "delivered_today": OrderSerializer(delivered_today_qs.order_by("-delivery_time"), many=True).data,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def available_orders_api(request):
    """
    1:1 с SupplierAvailableOrdersView.get:
    готови за вземане: status='ready_for_pickup'
    """
    bad = _ensure_supplier_type(request)
    if bad:
        return bad

    supplier, err = _ensure_supplier_profile(request)
    if err:
        return err

    available_orders = Order.objects.filter(status="ready_for_pickup").order_by("order_date_time")

    return Response({
        "current_time": timezone.now().isoformat(),
        "available_orders": OrderSerializer(available_orders, many=True).data
    })


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def edit_supplier_profile_api(request):
    """
    1:1 с EditSupplierProfileView:
    - GET: връща профила
    - PUT/PATCH: update профил
    """
    bad = _ensure_supplier_type(request)
    if bad:
        return bad

    supplier, err = _ensure_supplier_profile(request)
    if err:
        return err

    if request.method == "GET":
        return Response(SupplierSerializer(supplier).data)

    partial = request.method == "PATCH"
    ser = SupplierSerializer(supplier, data=request.data, partial=partial)
    ser.is_valid(raise_exception=True)
    ser.save()

    return Response({"status": "ok", "supplier": ser.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_order_api(request, order_id: int):
    """
    1:1 с accept_order:
    - само supplier
    - order трябва да е ready_for_pickup
    - set supplier + status on_delivery
    """
    bad = _ensure_supplier_type(request)
    if bad:
        return bad

    supplier, err = _ensure_supplier_profile(request)
    if err:
        return err

    order = get_object_or_404(Order, id=order_id)

    if order.status != "ready_for_pickup":
        return Response({"detail": "Поръчката не е налична за вземане"}, status=403)

    order.status = "on_delivery"
    order.supplier = supplier
    order.save(update_fields=["status", "supplier"])

    return Response({
        "status": "ok",
        "order": OrderSerializer(order).data,
        "next": "supplier_active_orders"
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def active_orders_api(request):
    """
    1:1 с supplier_active_orders:
    - orders за текущия supplier със status on_delivery
    """
    bad = _ensure_supplier_type(request)
    if bad:
        return bad

    supplier, err = _ensure_supplier_profile(request)
    if err:
        return err

    active_orders = Order.objects.filter(
        supplier=supplier,
        status="on_delivery"
    ).order_by("order_date_time")

    return Response({
        "active_orders": OrderSerializer(active_orders, many=True).data
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_delivered_api(request, order_id: int):
    """
    1:1 с mark_as_delivered:
    - само supplier
    - order трябва да е на този supplier
    - status трябва да е on_delivery
    - set status delivered
    """
    bad = _ensure_supplier_type(request)
    if bad:
        return bad

    supplier, err = _ensure_supplier_profile(request)
    if err:
        return err

    order = get_object_or_404(Order, id=order_id)

    if order.supplier_id != supplier.id:
        return Response({"detail": "Тази поръчка не е ваша"}, status=403)

    if order.status != "on_delivery":
        return Response({"detail": "Невалидна операция"}, status=403)

    order.status = "delivered"
    # хубаво е да запишеш и delivery_time ако не го правиш другаде
    if not order.delivery_time:
        order.delivery_time = timezone.now()

    order.save(update_fields=["status", "delivery_time"])

    return Response({
        "status": "ok",
        "order": OrderSerializer(order).data,
        "next": "supplier_active_orders"
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def delivered_orders_api(request):
    """
    1:1 с supplier_delivered_orders:
    доставени поръчки за текущия supplier
    """
    bad = _ensure_supplier_type(request)
    if bad:
        return bad

    supplier, err = _ensure_supplier_profile(request)
    if err:
        return err

    delivered_orders = Order.objects.filter(
        supplier=supplier,
        status="delivered"
    ).order_by("-delivery_time")

    return Response({
        "delivered_orders": OrderSerializer(delivered_orders, many=True).data
    })