from django.db import models

class DailyRevenue(models.Model):
    date = models.DateField()
    daily_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    account_type = models.CharField(max_length=20)
