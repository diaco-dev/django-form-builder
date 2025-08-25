from importlib import import_module

from django.apps import AppConfig


class MailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mail'

    def ready(self):
        import_module("mail.signals")  # from address import signals
        # invalidate_all()
