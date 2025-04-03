from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):
    ACCOUNT_TYPES = [
        ('supplier', 'Supplier'),
        ('restaurant', 'Restaurant'),
        ('user', 'User'),
    ]

    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)

    def __str__(self):
        return f"{self.username} ({self.type})"
