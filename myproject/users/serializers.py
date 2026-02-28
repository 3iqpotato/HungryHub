
from rest_framework import serializers


from myproject.users.models import UserProfile
from myproject.orders.models import Cart, Order  # CartItem може да е в orders.models при теб
from myproject.restaurants.models import Restaurant
# ---------- Serializers ----------

class UserProfileSerializer(serializers.ModelSerializer):
    profile_completed = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ("id", "img", "name", "phone_number", "address", "profile_completed")

    def get_profile_completed(self, obj):
        return obj.is_complete()

# # TODO ima da se opraci i da se ozpolzva istinskiq
# class RestaurantMiniSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Restaurant
#         # ако Restaurant има други имена, ще ги сменим
#         fields = ("id", "name")
#
# # TODO ima da se opraci i da se ozpolzva istinskiq
# class OrderMiniSerializer(serializers.ModelSerializer):
#     restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
#
#     class Meta:
#         model = Order
#         # ако полетата ти са различни, ще ги нагласим
#         fields = ("id", "status", "total_price", "order_date_time", "restaurant", "restaurant_name")


# ⚠️ Cart/CartItem част: тук може да се наложи да сменим имена на полета.
# class CartItemMiniSerializer(serializers.Serializer):
#     article_id = serializers.IntegerField()
#     article_name = serializers.CharField()
#     price = serializers.DecimalField(max_digits=10, decimal_places=2)
#     quantity = serializers.IntegerField()
