# -*- coding: utf-8 -*-

from celery.app import app_or_default

celery_app = app_or_default()

def celery_viestikanava(session_key):
  return f'ilmoitus.uusi.{session_key}'
