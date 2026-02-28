from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from myproject.articles.models import Article
from myproject.restaurants.models import Menu

from myproject.articles.serializers import ArticleSerializer, ArticleCreateUpdateSerializer


def _ensure_restaurant_account(request):
    if request.user.type != "restaurant":
        return Response({"detail": "Този endpoint е само за ресторант"}, status=403)
    # очакваме да имаш Restaurant профил: request.user.restaurant
    if not hasattr(request.user, "restaurant"):
        return Response({"detail": "Нямате попълнен ресторант профил"}, status=403)
    return None


def _ensure_menu_is_owned_by_restaurant(request, menu: Menu):
    if menu.restaurant_id != request.user.restaurant.id:
        return Response({"detail": "Нямате достъп до това меню"}, status=403)
    return None


def _ensure_article_is_owned_by_restaurant(request, article: Article):
    if article.menu.restaurant_id != request.user.restaurant.id:
        return Response({"detail": "Нямате достъп до този артикул"}, status=403)
    return None


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def article_add_api(request, menu_id: int):
    """
    POST /api/articles/article/add/<menu_id>/
    Body JSON:
    {
      "name": "...",
      "img": null,
      "type": "salads",
      "ingredients": "...",
      "price": "12.50",
      "weight": 250
    }
    """
    bad = _ensure_restaurant_account(request)
    if bad:
        return bad

    menu = get_object_or_404(Menu, id=menu_id)
    bad = _ensure_menu_is_owned_by_restaurant(request, menu)
    if bad:
        return bad

    ser = ArticleCreateUpdateSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    article = ser.save(menu=menu)

    return Response(
        {"status": "ok", "article": ArticleSerializer(article).data, "next": "restaurant_menu_edit", "menu_id": menu.id},
        status=status.HTTP_201_CREATED
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def article_edit_api(request, pk: int):
    """
    PUT/PATCH /api/articles/article/<pk>/edit/
    Body JSON (partial ok):
    {
      "name": "...",
      "price": "10.00"
    }
    """
    bad = _ensure_restaurant_account(request)
    if bad:
        return bad

    article = get_object_or_404(Article, pk=pk)
    bad = _ensure_article_is_owned_by_restaurant(request, article)
    if bad:
        return bad

    partial = request.method == "PATCH"
    ser = ArticleCreateUpdateSerializer(article, data=request.data, partial=partial)
    ser.is_valid(raise_exception=True)
    article = ser.save()

    return Response({
        "status": "ok",
        "article": ArticleSerializer(article).data,
        "next": "restaurant_menu_edit",
        "menu_id": article.menu_id
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def article_delete_api(request):
    """
    POST /api/articles/article/delete/
    Body JSON:
    { "delete_article": 123 }

    (1:1 с твоя ArticleDeleteView, който взима POST.get('delete_article'))
    """
    bad = _ensure_restaurant_account(request)
    if bad:
        return bad

    article_id = request.data.get("delete_article")
    if not article_id:
        return Response({"detail": "Липсва delete_article"}, status=400)

    article = get_object_or_404(Article, id=article_id)
    bad = _ensure_article_is_owned_by_restaurant(request, article)
    if bad:
        return bad

    menu_id = article.menu_id
    article.delete()

    return Response({
        "status": "ok",
        "deleted_article_id": int(article_id),
        "next": "restaurant_menu_edit",
        "menu_id": menu_id
    })