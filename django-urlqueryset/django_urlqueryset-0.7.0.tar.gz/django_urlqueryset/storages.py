import mimetypes
import os
from tempfile import SpooledTemporaryFile

import magic
import requests
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.utils.functional import LazyObject

from .utils import get_default_params


@deconstructible
class UrlStorage(FileSystemStorage):
    def get_available_name(self, name, *args, **kwargs):
        return name

    def get_params(self):
        params = get_default_params()
        params.pop('fetch_method')
        return params

    def _open(self, url, mode='rb'):
        params = self.get_params()
        params['url'] = url
        file = SpooledTemporaryFile(mode='b')
        file.write(requests.get(**params).content)
        file.seek(0)
        return File(file, mode)

    def _save(self, url, content):
        params = self.get_params()
        params['url'] = url
        params.setdefault('headers', {})['Content-Type'] = magic.from_buffer(content.read(100), mime=True)
        content.seek(0)
        response = requests.post(data=content.read(), **params)
        response.raise_for_status()
        return url

    def exists(self, name):
        return True

    def listdir(self, path):
        return [], []

    def url(self, name):
        return name


class DefaultStorage(LazyObject):
    def _setup(self):
        self._wrapped = UrlStorage()


default_storage = DefaultStorage()
