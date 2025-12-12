from django.apps import AppConfig
from django.core.management import call_command
from django.db.utils import OperationalError, ProgrammingError


class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'

    def ready(self):
        try:
            call_command('create_default_superuser')
        except (OperationalError, ProgrammingError):
            # Database might not be ready during migrate/collectstatic
            pass
