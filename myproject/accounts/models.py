from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class AccountManager(BaseUserManager):
    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        if not username:
            raise ValueError('The Username must be set')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class Account(AbstractUser):
    ACCOUNT_TYPES = [
        ('supplier', 'Supplier'),
        ('restaurant', 'Restaurant'),
        ('user', 'User'),
    ]

    username = models.CharField(max_length=150, unique=True)  # Вече не е nullable
    email = models.EmailField(unique=True)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'type']  # Добавяме username тук

    objects = AccountManager()

    def __str__(self):
        return f"{self.username} ({self.email})"
