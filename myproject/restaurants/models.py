from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum
from django.utils.timezone import now


class Restaurant(models.Model):
    account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    img = models.ImageField(upload_to='restaurants/', null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    rating = models.FloatField(default=0, validators=[MaxValueValidator(5.0), MinValueValidator(0.0)])
    delivery_fee = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00, blank=True,
        validators=[
            MinValueValidator(0.00),
            MaxValueValidator(10.00)
        ]
    )
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def get_daily_turnover(self, date=None):
        from myproject.orders.models import Order  # вътрешен импорт!
        date = date or now().date()
        return Order.objects.filter(
            restaurant=self,
            status='delivered',
            delivery_time__date=date
        ).aggregate(total=Sum('order_items__article__price'))['total'] or 0

    def get_monthly_turnover(self, year=None, month=None):
        from myproject.orders.models import Order  # вътрешен импорт!
        now_ = now()
        year = year or now_.year
        month = month or now_.month
        return Order.objects.filter(
            restaurant=self,
            status='delivered',
            delivery_time__year=year,
            delivery_time__month=month
        ).aggregate(total=Sum('order_items__article__price'))['total'] or 0

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="NO name")
    # ще се свърже чрез M2M с артикули
