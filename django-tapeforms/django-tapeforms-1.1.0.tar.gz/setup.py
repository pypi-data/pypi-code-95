# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tapeforms', 'tapeforms.contrib', 'tapeforms.templatetags']

package_data = \
{'': ['*'],
 'tapeforms': ['templates/tapeforms/fields/*',
               'templates/tapeforms/includes/*',
               'templates/tapeforms/layouts/*',
               'templates/tapeforms/widgets/*']}

install_requires = \
['Django>=2.2']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata'], 'docs': ['Sphinx>=3.5']}

setup_kwargs = {
    'name': 'django-tapeforms',
    'version': '1.1.0',
    'description': 'A helper to render Django forms using HTML templates.',
    'long_description': "django-tapeforms\n================\n\n.. image:: https://img.shields.io/pypi/v/django-tapeforms.svg\n   :target: https://pypi.org/project/django-tapeforms/\n   :alt: Latest Version\n\n.. image:: https://github.com/stephrdev/django-tapeforms/workflows/Test/badge.svg?branch=master\n   :target: https://github.com/stephrdev/django-tapeforms/actions?workflow=Test\n   :alt: CI Status\n\n.. image:: https://codecov.io/gh/stephrdev/django-tapeforms/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/stephrdev/django-tapeforms\n   :alt: Coverage Status\n\n.. image:: https://readthedocs.org/projects/django-tapeforms/badge/?version=latest\n   :target: https://django-tapeforms.readthedocs.io/en/stable/?badge=latest\n   :alt: Documentation Status\n\n\nUsage\n-----\n\nPlease refer to the `Documentation <https://django-tapeforms.readthedocs.io/>`_ to\nlearn how to use ``django-tapeforms``. Basicly, ``tapeforms`` provides a mixin\nand some Django template tags to help you render your forms to HTML.\n\n\nRequirements\n------------\n\ndjango-tapeforms supports Python 3 only and requires at least Django 2.2.\nNo other dependencies are required.\n\n\nPrepare for development\n-----------------------\n\nA Python 3.6 interpreter is required in addition to pipenv.\n\n.. code-block:: shell\n\n    $ poetry install\n\n\nNow you're ready to start the example project to experiment with tapeforms.\n\n.. code-block:: shell\n\n    $ poetry run python examples/manage.py runserver\n",
    'author': 'Stephan Jaekel',
    'author_email': 'steph@rdev.info',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/stephrdev/django-tapeforms',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4',
}


setup(**setup_kwargs)
