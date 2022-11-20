from django.apps import AppConfig


class ServerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'server'

    def ready(self):
        from .ap_scheduler import start
        start()
