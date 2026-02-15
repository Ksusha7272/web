from django.apps import AppConfig
from django.apps import AppConfig


class GalleryConfig(AppConfig):
    name = 'gallery'

class GalleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gallery'
    # Этот метод запускается один раз при старте сервера
    def ready(self):
        import gallery.signals # Импортируем наш файл с сигналами