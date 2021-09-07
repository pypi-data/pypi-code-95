from django.conf import settings


settings.SERVITIN_FORMATTER_DEBUG = getattr(settings, 'SERVITIN_FORMATTER_DEBUG', False)

settings.SERVITIN_LOGGING = getattr(settings, 'SERVITIN_LOGGING', {
    'formatters': {
        'servitin_default': {
            'format': '%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        }
    }
})
