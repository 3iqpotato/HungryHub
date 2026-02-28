from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from .models import Order


@receiver(pre_save, sender=Order)
def update_supplier_earnings(sender, instance, **kwargs):
    # ако е нов обект – няма как да е delivered преди
    if not instance.pk:
        return

    try:
        old_instance = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return

    # начисляваме САМО ако:
    # - старият статус НЕ е delivered
    # - новият статус е delivered
    if old_instance.status != 'delivered' and instance.status == 'delivered' and instance.supplier:
        supplier = instance.supplier
        today = timezone.now().date()

        if supplier.last_reset != today:
            supplier.daily_earnings = 0
            supplier.last_reset = today

        supplier.daily_earnings += Decimal('3.00')
        supplier.save()