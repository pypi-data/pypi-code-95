# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
  setup_requires='git-versiointi',
  name='django-celery-ilmoitus',
  description='Ajax/Websocket-pohjainen Django-ilmoitusnäkymä',
  url='https://github.com/an7oine/django-celery-ilmoitus.git',
  author='Antti Hautaniemi',
  author_email='antti.hautaniemi@me.com',
  packages=find_packages(),
  include_package_data=True,
  zip_safe=False,
  install_requires=['celery', 'Django'],
  extras_require={
    'websocket': ['django-pistoke'],
  },
  entry_points={
    'django.sovellus': 'ilmoitus = ilmoitus.sovellus:Ilmoitus',
    'django.osoitteet': 'ilmoitus = ilmoitus.nakyma',
  },
)
