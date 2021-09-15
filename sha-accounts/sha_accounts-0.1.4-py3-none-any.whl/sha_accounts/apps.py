from django.apps import AppConfig


class ShaAccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sha_accounts'

    def ready(self):
        import sha_accounts.signals
