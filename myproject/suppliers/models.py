from django.db import models
from django.conf import settings

class Supplier(models.Model):
    account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    img = models.ImageField(upload_to='suppliers/', null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    type = models.CharField(max_length=50)
