from django.apps import AppConfig


class SucursalesConfig(AppConfig):
    name = 'sucursales'

class SucursalesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sucursales'

    def ready(self):
        import sucursales.signals

