from django.apps import AppConfig


class RestaurantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myproject.restaurants'

    def ready(self):
        import myproject.restaurants.signals