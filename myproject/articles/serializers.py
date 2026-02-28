from rest_framework import serializers
from myproject.articles.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    menu_id = serializers.IntegerField(source="menu.id", read_only=True)
    restaurant_id = serializers.IntegerField(source="menu.restaurant.id", read_only=True)
    restaurant_name = serializers.CharField(source="menu.restaurant.name", read_only=True)

    class Meta:
        model = Article
        fields = (
            "id",
            "name",
            "img",
            "type",
            "ingredients",
            "price",
            "rating",
            "weight",
            "menu",
            "menu_id",
            "restaurant_id",
            "restaurant_name",
        )


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    За create/edit – можеш да ограничиш полетата и да не връщаш излишни computed fields.
    """
    class Meta:
        model = Article
        fields = ("name", "img", "type", "ingredients", "price", "rating", "weight", "menu")