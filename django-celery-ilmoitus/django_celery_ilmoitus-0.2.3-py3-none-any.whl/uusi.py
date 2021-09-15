# -*- coding: utf-8 -*-

from contextlib import contextmanager
from importlib import import_module

from django.conf import settings
from django.contrib.messages.storage import default_storage

from .celery import celery_app, celery_viestikanava


@contextmanager
def tallenna_asynkroninen_ilmoitus(session_key):
  '''
  Kontekstikäsittelijä viestin lähettämiseen käyttäjälle HTTP-pyynnön
  ulkopuolelta, esim. asynkronisen tausta-ajon yhteydessä.
  '''
  # Hae käyttäjän istunto ja muodosta keinotekoinen HTTP-pyyntö.
  try:
    class Pyynto:
      session = import_module(settings.SESSION_ENGINE).SessionStore(session_key)
    request = Pyynto()
    store = default_storage(request)
  except:
    store = None
    raise
  finally:
    # Suoritetaan haluttu toiminto kontekstin sisällä, vaikka viestiajurin
    # muodostus epäonnistuisi. Tällöin `store` on `None`.
    try:
      yield store
    finally:
      if store is not None:
        # Pakota viestien ja istunnon tallennus,
        # sillä tavanomaista HTTP-paluusanomaa ei ole käytettävissä.
        store.update(None)
        request.session.save()
        # Lähetä Celery-signaali, jotta käyttäjän mahdollinen avoin istunto
        # saa reaaliaikaisen tiedon uudesta viestistä.
        channel = celery_app.broker_connection().channel()
        dispatcher = celery_app.events.Dispatcher(channel=channel)
        dispatcher.send(type=celery_viestikanava(session_key))
        # if store is not None
      # finally
    # finally
  # def tallenna_asynkroninen_ilmoitus
