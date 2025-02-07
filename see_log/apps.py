import os

from django.apps import AppConfig


class SeeLogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'see_log'

    def ready(self):
        run_main = os.environ.get('RUN_MAIN', None)
        print(f"应用see_log加载完成,run_main环境变量是: {run_main}")
