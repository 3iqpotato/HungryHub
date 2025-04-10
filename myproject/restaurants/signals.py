# restaurants/signals.py
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Restaurant, Menu

@receiver(post_save, sender=Restaurant)
def create_restaurant_menu(sender, instance, created, **kwargs):
    if created:
        Menu.objects.create(restaurant=instance, name=f"Меню на {instance.name}")

@receiver(pre_delete, sender=Restaurant)
def delete_restaurant_menu(sender, instance, **kwargs):
    if hasattr(instance, 'menu'):
        instance.menu.delete()

# Важно: Регистрирайте сигналите в apps.py