from django.db import models
from myproject.restaurants.models import Menu

class Article(models.Model):
    # Define dropdown choices for "type"
    TYPE_CHOICES = [
        ('salads', 'Salads'),
        ('appetizers', 'Appetizers'),
        ('main_course', 'Main Course'),
        ('desserts', 'Desserts'),
    ]

    name = models.CharField(max_length=100)
    img = models.ImageField(upload_to='articles/', null=True, blank=True)
    type = models.CharField(
        max_length=20,  # Reduced max_length to match the longest choice ('main_course')
        choices=TYPE_CHOICES,  # Add dropdown options
        default='main_course'  # Optional: Set a default
    )
    ingredients = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    rating = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    # category = models.CharField(max_length=50, null=True, blank=True)
    menu = models.ForeignKey(  # Променено от ManyToManyField
        Menu,
        on_delete=models.CASCADE,
        related_name='articles'
    )
