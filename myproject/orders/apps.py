from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myproject.orders'

    def ready(self):
        import myproject.orders.signals  # зареждаме сигналите при стартиране