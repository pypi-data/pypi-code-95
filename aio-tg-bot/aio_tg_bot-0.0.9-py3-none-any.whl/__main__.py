import os
import pathlib
import aiogram


def setup(dispatcher, filter=True, middleware=True, use_django=False):
    from . import filters
    from . import middlewares
    from . import fsm_storage
    from .etc.database import models
    from .etc.database.migrations import Router

    dispatcher.storage = fsm_storage.PeeweeORMStorage()

    if filter:
        filters.setup(dispatcher)
    if middleware:
        middlewares.setup(dispatcher)
    if use_django:
        import django
        django.setup()
