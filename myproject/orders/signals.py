from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from .models import Order


@receiver(post_save, sender=Order)
def update_supplier_earnings(sender, instance, created, **kwargs):
    if instance.status == 'delivered' and instance.supplier:
        supplier = instance.supplier
        today = timezone.now().date()

        if supplier.last_reset != today:
            supplier.daily_earnings = 0
            supplier.last_reset = today

        supplier.daily_earnings += Decimal('3.00')
        supplier.save()
