from django.db import models
from django.conf import settings
from django.utils.timezone import now

class Supplier(models.Model):
    account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    img = models.ImageField(upload_to='suppliers/', null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    type = models.CharField(max_length=50)

    def get_daily_earnings(self, date=None, bonus_threshold=200):
        from myproject.orders.models import Order  # вътрешен импорт!
        date = date or now().date()
        orders = Order.objects.filter(
            supplier=self,
            status='delivered',
            delivery_time__date=date
        )
        total = sum(order.get_total_price() for order in orders)
        bonus = 20 if total > bonus_threshold else 0
        return {
            'orders': orders,
            'total': total,
            'bonus': bonus
        }
