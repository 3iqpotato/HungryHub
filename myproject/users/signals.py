from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile
from myproject.orders.models import Cart

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile_and_cart(sender, instance, created, **kwargs):
    """Създава UserProfile и Cart при регистрация на нов потребител."""
    if created and instance.type == 'user':  # Само за обикновени потребители
        UserProfile.objects.create(account=instance)
        Cart.objects.create(user=instance)  # Създава празна количка

@receiver(pre_delete, sender=UserProfile)
def delete_user_cart(sender, instance, **kwargs):
    """Изтрива Cart при изтриване на UserProfile."""
    try:
        cart = Cart.objects.get(user=instance.account)
        cart.delete()
    except Cart.DoesNotExist:
        pass