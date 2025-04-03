from django.db import models
from myproject.users.models import UserProfile
from myproject.suppliers.models import Supplier
from myproject.restaurants.models import Restaurant
from myproject.articles.models import Article

class Cart(models.Model):
    items = models.ManyToManyField(Article)
    price = models.DecimalField(max_digits=8, decimal_places=2)

class Order(models.Model):
    address_for_delivery = models.TextField()
    order_date_time = models.DateTimeField()
    delivery_time = models.DateTimeField()
    status = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True)
