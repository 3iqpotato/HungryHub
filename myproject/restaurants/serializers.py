from rest_framework import serializers
from myproject.restaurants.models import Restaurant, Menu


class RestaurantMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ("id", "name", "img", "rating", "delivery_fee", "discount")


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = (
            "id",
            "name",
            "img",
            "phone_number",
            "address",
            "rating",
            "delivery_fee",
            "discount",
        )


class MenuSerializer(serializers.ModelSerializer):
    restaurant_id = serializers.IntegerField(source="restaurant.id", read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)

    class Meta:
        model = Menu
        fields = ("id", "name", "restaurant", "restaurant_id", "restaurant_name")