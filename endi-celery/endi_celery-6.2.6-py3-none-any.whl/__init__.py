# -*- coding:utf-8 -*-
import locale
locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

import logging
from pyramid.config import Configurator
from pyramid.paster import setup_logging
from sqlalchemy import engine_from_config
from pyramid_beaker import set_cache_regions_from_settings

from endi import (
    prepare_view_config,
    configure_filedepot,
)
from endi.models import *
from endi_base.models.initialize import initialize_sql
from endi_celery.tasks.csv_import import (
    MODELS_CONFIGURATION as IMPORT_MODELS_CONFIGURATION,
)
from endi_celery.tasks.export import (
    MODELS_CONFIGURATION as EXPORT_MODELS_CONFIGURATION
)


def register_import_model(
    config, key, model, label, permission, excludes,
    callbacks=()
):
    """
    Register a model for import

    :param obj config: The pyramid configuration object
    :param str key: The key used to identify the model type
    :param class model: The model to be used
    :param str label: A label describing the type of datas
    :param str permission: The permission to associate to this import
    :param tuple excludes: The field of the model we don't want to handle in
    the import
    :param list callbacks: List of callables called after import action
    """
    IMPORT_MODELS_CONFIGURATION[key] = {
        'factory': model,
        'label': label,
        'permission': permission,
        'excludes': excludes,
        'callbacks': callbacks,
    }


def register_export_model(config, key, model, options={}):
    """
    Register a model for export

    :param obj config: The pyramid configuration object
    :param str key: The key used to identify the model type
    :param class model: The model to be used
    """
    EXPORT_MODELS_CONFIGURATION[key] = {'factory': model}
    EXPORT_MODELS_CONFIGURATION[key].update(options)


def includeme(config):
    """
    Includes some celery specific stuff in the main application
    """
    config.add_directive("register_import_model", register_import_model)
    config.add_directive("register_export_model", register_export_model)
    config.include("endi_celery.tasks")


def worker(global_config, **settings):
    """
    Entry point for the pyramid celery stuff
    """
    logging.basicConfig()
    setup_logging(global_config['__file__'])
    logger = logging.getLogger(__name__)
    logger.info("Bootstraping app")
    engine = engine_from_config(settings, 'sqlalchemy.')
    set_cache_regions_from_settings(settings)
    dbsession = initialize_sql(engine)
    config = Configurator(settings=settings)
    # config.include('pyramid_celery')
    includeme(config)

    config.configure_celery(global_config['__file__'])
    config.commit()

    config = prepare_view_config(
        config, dbsession, from_tests=False, **settings
    )
    configure_filedepot(settings)
    config.include('endi.views.files')
    return config.make_wsgi_app()


def scheduler(global_config, **settings):
    logging.basicConfig()
    setup_logging(global_config['__file__'])
    logger = logging.getLogger(__name__)
    logger.info("Bootstraping celery scheduler application")
    config = Configurator(settings=settings)
    config.include('pyramid_celery')
    config.configure_celery(global_config['__file__'])
    config.commit()
    return config.make_wsgi_app()
