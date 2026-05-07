from django.apps import AppConfig

class OrderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.order'
    label = 'order'

    def ready(self):
        import apps.order.signals  # noqa: F401
