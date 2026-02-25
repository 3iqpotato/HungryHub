from decimal import Decimal

from django.db import models
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone



class Supplier(models.Model):
    TRANSPORT_CHOICES = [
        ('car', 'Кола'),
        ('motorcycle', 'Мотор'),
        ('bicycle', 'Велосипед'),
        ('other', 'Друг'),
    ]

    account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    img = models.ImageField(upload_to='suppliers/', null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    type = models.CharField(
        max_length=20,
        choices=TRANSPORT_CHOICES,
        blank=True,
        null=True
    )

    daily_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_reset = models.DateField(default=timezone.now)

    def get_daily_earnings(self, date=None):
        from myproject.orders.models import Order
        from myproject.orders.models import OrderItem

        date = date or timezone.now().date()

        agg = Order.objects.filter(
            supplier=self,
            status='delivered',
            delivery_time__date=date
        ).aggregate(
            deliveries=Count('id'),
            small_orders=Count('id', filter=Q(delivery_fee__gt=0))
        )

        deliveries = agg['deliveries'] or 0
        small_orders = agg['small_orders'] or 0

        base_pay = deliveries * Decimal("2.00")
        small_order_bonus = small_orders * Decimal("1.00")

        return base_pay + small_order_bonus

    def get_monthly_earnings(self, year=None, month=None):
        from myproject.orders.models import Order

        now_ = timezone.now()
        year = year or now_.year
        month = month or now_.month

        agg = Order.objects.filter(
            supplier=self,
            status='delivered',
            delivery_time__year=year,
            delivery_time__month=month
        ).aggregate(
            deliveries=Count('id'),
            small_orders=Count('id', filter=Q(delivery_fee__gt=0))
        )

        deliveries = agg['deliveries'] or 0
        small_orders = agg['small_orders'] or 0

        base_pay = deliveries * Decimal("2.00")
        small_order_bonus = small_orders * Decimal("1.00")

        return base_pay + small_order_bonus


    # def get_daily_turnover(self, date=None):
    #     from myproject.orders.models import OrderItem
    #     from django.utils.timezone import now
    #     from django.db.models import Sum, F, ExpressionWrapper, DecimalField
    #
    #     date = date or now().date()
    #
    #     return OrderItem.objects.filter(
    #         order__supplier=self,
    #         order__status='delivered',
    #         order__delivery_time__date=date
    #     ).annotate(
    #         total_price=ExpressionWrapper(
    #             F('quantity') * F('article__price'),
    #             output_field=DecimalField()
    #         )
    #     ).aggregate(total=Sum('total_price'))['total'] or 0
    #
    # def get_monthly_turnover(self, year=None, month=None):
    #     from myproject.orders.models import OrderItem
    #     from django.utils.timezone import now
    #     from django.db.models import Sum, F, ExpressionWrapper, DecimalField
    #
    #     now_ = now()
    #     year = year or now_.year
    #     month = month or now_.month
    #
    #     return OrderItem.objects.filter(
    #         order__supplier=self,
    #         order__status='delivered',
    #         order__delivery_time__year=year,
    #         order__delivery_time__month=month
    #     ).annotate(
    #         total_price=ExpressionWrapper(
    #             F('quantity') * F('article__price'),
    #             output_field=DecimalField()
    #         )
    #     ).aggregate(total=Sum('total_price'))['total'] or 0

    # def calculate_bonus(self):
    #     daily_turnover = self.get_daily_turnover()
    #     return (daily_turnover // 100) * 5



