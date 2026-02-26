from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def _next_for_user(user):
    """
    Връща къде да отиде мобилното (екран/route) според типа и дали има попълнен профил.
    Тук имитираме логиката на CustomLoginView.get_success_url + complete_profile_redirect.
    """
    # type: user
    if user.type == "user":
        if hasattr(user, "userprofile") and user.userprofile.is_complete():
            return {
                "next": "user_home",
                "profile_id": getattr(user.userprofile, "id", None),
            }
        return {"next": "complete_user_profile"}

    # type: supplier
    if user.type == "supplier":
        if hasattr(user, "supplier"):
            return {"next": "supplier_home"}
        return {"next": "complete_supplier_profile"}

    # type: restaurant
    if user.type == "restaurant":
        if hasattr(user, "restaurant"):
            return {
                "next": "restaurant_home",
                "profile_id": getattr(user.restaurant, "id", None),
            }
        return {"next": "complete_restaurant_profile"}

    # fallback
    return {"next": "complete_profile"}


@api_view(["POST"])
@permission_classes([AllowAny])
def register_api(request):
    """
    JSON body:
    {
      "email": "...",
      "password": "...",
      "type": "user" | "supplier" | "restaurant",
      "username": "..."   (по желание; ако липсва -> ще стане email)
    }
    """
    print(request.data)
    email = (request.data.get("email") or "").strip().lower() # може да има проблем с lower TODO
    password = request.data.get("password") or ""
    acc_type = (request.data.get("type") or "").strip()
    username = (request.data.get("username") or "").strip()

    if not email or not password or not acc_type:
        return Response(
            {"detail": "email, password и type са задължителни"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if acc_type not in {"user", "supplier", "restaurant"}:
        return Response({"detail": "Невалиден type"}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"detail": "Този email вече съществува"}, status=400)

    # при теб username често = email
    if not username:
        username = email

    # ВАЖНО: твоят Account има USERNAME_FIELD='email', така че create_user приема email като "username" параметър НЕ винаги.
    # За да не гадаем сигнатурата на manager-а, създаваме директно:
    user = User(email=email, username=username, type=acc_type)
    user.set_password(password)
    user.save()

    data = {
        "user": {"id": user.id, "email": user.email, "username": user.username, "type": user.type},
        **_tokens_for_user(user),
        **_next_for_user(user),
    }
    return Response(data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_api(request):
    """
    JSON body:
    { "email": "...", "password": "..." }

    Връща JWT + next.
    """
    email = (request.data.get("email") or "").strip().lower()
    password = request.data.get("password") or ""

    if not email or not password:
        return Response({"detail": "email и password са задължителни"}, status=400)

    # authenticate работи с USERNAME_FIELD. При теб това е email.
    user = authenticate(request, email=email, password=password)

    # ако backend-ът ти очаква username вместо email, това ще върне None.
    # тогава ще го оправим с custom auth backend (казвам ти по-долу).
    if not user:
        return Response({"detail": "Грешен email или парола"}, status=status.HTTP_401_UNAUTHORIZED)

    data = {
        "user": {"id": user.id, "email": user.email, "username": user.username, "type": user.type},
        **_tokens_for_user(user),
        **_next_for_user(user),
    }
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api(request):
    # JWT logout е клиентски: MAUI трие токените.
    return Response({"detail": "OK"})