# -*- coding: utf-8 -*-

import asyncio
import json
import socket

from asgiref.sync import async_to_sync, sync_to_async

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import get_messages
from django.contrib.messages.storage import default_storage
from django.http import JsonResponse
from django.urls import path
from django.views import generic

from .celery import celery_app, celery_viestikanava


class Ilmoitukset(LoginRequiredMixin, generic.View):

  bootstrap_luokat = {
    'debug': 'alert-info',
    'info': 'alert-info',
    'success': 'alert-success',
    'warning': 'alert-warning',
    'error': 'alert-danger',
  }

  def _ilmoitus(self, ilmoitus):
    ''' Muodosta JSON-yhteensopiva sanoma ilmoituksen tiedoin. '''
    return {
      'level': ilmoitus.level,
      'message': ilmoitus.message,
      'tags': ' '.join((
        self.bootstrap_luokat.get(luokka, luokka)
        for luokka in ilmoitus.tags.split(' ')
      ))
    }
    # def _ilmoitus

  def get(self, request, *args, **kwargs):
    ''' Ajax-toteutus. Palauta JSON-sanoma kaikista ilmoituksista. '''
    # pylint: disable=unused-argument
    storage = get_messages(request)
    return JsonResponse([
      self._ilmoitus(ilmoitus)
      for ilmoitus in storage
    ], safe=False)
    # def get

  async def websocket(self, request):
    '''
    Websocket-toteutus. Palauta ilmoituksia sitä mukaa, kun niitä tallennetaan.
    '''
    async def laheta_ilmoitukset(signaali=None):
      ''' Lähetä kaikki olemassaolevat ilmoitukset selaimelle. '''
      # pylint: disable=unused-argument
      def hae_ilmoitukset():
        # pylint: disable=protected-access
        request.session._session_cache = request.session.load()
        request._messages = default_storage(request)
        for ilmoitus in request._messages:
          yield json.dumps(self._ilmoitus(ilmoitus))
        request._messages.update(None)
        request.session.save()
        # def hae_ilmoitukset
      for ilmoitus in await sync_to_async(lambda: list(hae_ilmoitukset()))():
        await request.send(ilmoitus)
        # for ilmoitus in await sync_to_async
      # async def laheta_ilmoitukset

    def celery_capture():
      try: receiver.capture(timeout=10)
      except socket.timeout: pass

    # Luo oma säikeensä Celery-signaalien kuunteluun.
    try:
      channel = celery_app.broker_connection().channel()
    except Exception:
      await request.send(json.dumps({'status': '500'}))
      raise

    # Aja Celery-viestien vastaanottorutiini taustalla.
    loop = asyncio.get_running_loop()
    receiver = celery_app.events.Receiver(channel=channel, handlers={
      celery_viestikanava(request.session.session_key):
      async_to_sync(laheta_ilmoitukset),
    })
    luku = loop.run_in_executor(None, celery_capture)

    # Lähetä mahdolliset olemassaolevat ilmoitukset heti.
    await laheta_ilmoitukset()

    # Kuuntele Celery-signaaleja, kunnes yhteys katkaistaan.
    try:
      await luku
    finally:
      receiver.should_stop = True
      await luku
    # async def websocket

  # class Ilmoitukset


urlpatterns = [
  path('', Ilmoitukset.as_view(), name='ilmoitukset'),
]
