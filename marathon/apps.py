from django.apps import AppConfig


class MarathonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'marathon'

    def ready(self):
        print("应用marathon加载完成")