from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

class Restaurant(models.Model):
    account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    img = models.ImageField(upload_to='restaurants/', null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    rating = models.FloatField(default=0, validators=[MaxValueValidator(5.0), MinValueValidator(0.0)])
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    # ще се свърже чрез M2M с артикули
