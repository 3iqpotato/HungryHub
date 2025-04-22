from numbers import Number

from django.db import models


from myproject.users.models import UserProfile
from myproject.suppliers.models import Supplier
from myproject.restaurants.models import Restaurant
from myproject.articles.models import Article

class Cart(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)  # Нова връзка

    def get_total_price(self):
        items = self.items.all()
        total = sum(item.get_total_price() for item in items)
        return total

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
        ('picked_up', 'Picked Up'),
    ]
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    address_for_delivery = models.TextField()
    order_date_time = models.DateTimeField()
    delivery_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True)

    def get_total_price(self):
        items = self.order_items.all()
        total = sum(item.get_total_price() for item in items)
        return total + (self.restaurant.delivery_fee if self.restaurant and hasattr(self.restaurant, 'delivery_fee') else 0)

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

