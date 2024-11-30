from django.apps import AppConfig


class SeeLogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'see_log'

    def ready(self):
        print("应用see_log加载完成")
