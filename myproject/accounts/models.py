from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Account(AbstractUser):
    ACCOUNT_TYPES = [
        ('supplier', 'Supplier'),
        ('restaurant', 'Restaurant'),
        ('user', 'User'),
    ]

    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['type']  # username не е задължителен, защото използваме email

    def __str__(self):
        return f"{self.email} ({self.type})"
