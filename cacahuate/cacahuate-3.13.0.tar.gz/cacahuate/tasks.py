import os
import logging
import traceback
from itacate import Config
from celery import Celery

from .handler import Handler

LOGGER = logging.getLogger(__name__)

config = Config(os.path.dirname(os.path.realpath(__file__)))
config.from_object('cacahuate.settings')

if os.getenv('CACAHUATE_SETTINGS'):
    config.from_envvar('CACAHUATE_SETTINGS', silent=False)

handler = Handler(config)
app = Celery()


@app.task(ignore_result=True)
def handle(body):
    try:
        handler(body)
    except Exception:
        LOGGER.error(traceback.format_exc())
