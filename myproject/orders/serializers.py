from rest_framework import serializers
from myproject.orders.models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    article_id = serializers.IntegerField(source="article.id", read_only=True)
    article_name = serializers.CharField(source="article.name", read_only=True)
    price = serializers.DecimalField(source="article.price", max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ("id", "article_id", "article_name", "price", "quantity", "total_price")

    def get_total_price(self, obj):
        return obj.get_total_price()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    delivery_fee = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ("id", "items", "subtotal", "delivery_fee", "total")

    def get_subtotal(self, obj):
        return obj.get_subtotal()

    def get_delivery_fee(self, obj):
        return obj.get_delivery_fee()

    def get_total(self, obj):
        return obj.get_total_price()


class OrderItemSerializer(serializers.ModelSerializer):
    article_id = serializers.IntegerField(source="article.id", read_only=True)
    article_name = serializers.CharField(source="article.name", read_only=True)
    price = serializers.DecimalField(source="article.price", max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ("id", "article_id", "article_name", "price", "quantity", "total_price")

    def get_total_price(self, obj):
        return obj.get_total_price()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source="order_items", many=True, read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "address_for_delivery",
            "order_date_time",
            "delivery_time",
            "delivery_fee",
            "total_price",
            "restaurant",
            "restaurant_name",
            "supplier",
            "supplier_name",
            "items",
        )