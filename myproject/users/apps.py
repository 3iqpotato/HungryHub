from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myproject.users'

    def ready(self):
        import myproject.users.signals  # Активира сигналите
