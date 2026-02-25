from decimal import Decimal
from numbers import Number

from django.db import models
from myproject.users.models import UserProfile
from myproject.suppliers.models import Supplier
from myproject.restaurants.models import Restaurant
from myproject.articles.models import Article

class Cart(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)  # Нова връзка

    def get_subtotal(self):
        items = self.items.all()
        return sum(item.get_total_price() for item in items)

    def get_delivery_fee(self):
        subtotal = self.get_subtotal()
        if subtotal > 0 and subtotal < Decimal("30.00"):
            return Decimal("3.00")
        return Decimal("0.00")

    def get_total_price(self):
        return self.get_subtotal() + self.get_delivery_fee()


    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    # Може да е в кошница или в поръчка — едно от двете
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', null=True, blank=True)

    def get_total_price(self):
        return self.article.price * self.quantity



class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('on_delivery', 'On Delivery'),
        ('delivered', 'Delivered'),
    ]
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    address_for_delivery = models.TextField()
    order_date_time = models.DateTimeField()
    delivery_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))


    # def get_total_price(self):
    #     items = self.order_items.all()
    #     total = sum(item.get_total_price() for item in items)
    #     return total + (self.restaurant.delivery_fee if self.restaurant and hasattr(self.restaurant, 'delivery_fee') else 0)

    def get_subtotal(self):
        return sum((item.get_total_price() for item in self.order_items.all()), Decimal("0.00"))

    # def calculate_delivery_fee(self):
    #     # Ако имаш нулеви поръчки – не начислявай
    #     subtotal = self.get_subtotal()
    #     if subtotal > 0 and subtotal < Decimal("30.00"):
    #         return Decimal("3.00")
    #     return Decimal("0.00")

    # def get_total_price(self):
    #     return self.get_subtotal() + (self.delivery_fee or Decimal("0.00"))


    @property
    def cart_items(self):
        return CartItem.objects.filter(order=self)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Примерно поле за количество

    def __str__(self):
        return f"{self.article.name} - {self.quantity}"

    def get_total_price(self):
        return self.article.price * self.quantity



