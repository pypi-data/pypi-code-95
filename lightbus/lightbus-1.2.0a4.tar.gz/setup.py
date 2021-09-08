# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lightbus',
 'lightbus.client',
 'lightbus.client.docks',
 'lightbus.client.internal_messaging',
 'lightbus.client.subclients',
 'lightbus.commands',
 'lightbus.config',
 'lightbus.plugins',
 'lightbus.schema',
 'lightbus.serializers',
 'lightbus.transports',
 'lightbus.transports.redis',
 'lightbus.utilities',
 'lightbus_vendored',
 'lightbus_vendored.jsonpath']

package_data = \
{'': ['*']}

install_requires = \
['aioredis>=1.2.0', 'jsonschema>=3.2', 'pyyaml>=3.12']

entry_points = \
{'console_scripts': ['lightbus = lightbus.commands:lightbus_entry_point'],
 'lightbus_event_transports': ['debug = lightbus:DebugEventTransport',
                               'redis = lightbus:RedisEventTransport'],
 'lightbus_plugins': ['internal_metrics = '
                      'lightbus.plugins.metrics:MetricsPlugin',
                      'internal_state = lightbus.plugins.state:StatePlugin'],
 'lightbus_result_transports': ['debug = lightbus:DebugResultTransport',
                                'redis = lightbus:RedisResultTransport'],
 'lightbus_rpc_transports': ['debug = lightbus:DebugRpcTransport',
                             'redis = lightbus:RedisRpcTransport'],
 'lightbus_schema_transports': ['debug = lightbus:DebugSchemaTransport',
                                'redis = lightbus:RedisSchemaTransport']}

setup_kwargs = {
    'name': 'lightbus',
    'version': '1.2.0a4',
    'description': 'RPC & event framework for Python 3',
    'long_description': "\nWhat is Lightbus?\n=================\n\n\n.. image:: https://img.shields.io/circleci/build/github/adamcharnock/lightbus\n   :target: https://circleci.com/gh/adamcharnock/lightbus/tree/master\n   :alt: CircleCI\n\n\n.. image:: https://api.codacy.com/project/badge/Grade/801d031fd2714b4f9c643182f1fbbd0b\n   :target: https://www.codacy.com/app/adamcharnock/lightbus?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=adamcharnock/lightbus&amp;utm_campaign=Badge_Grade\n   :alt: Codacy Badge\n\n\n.. image:: https://api.codacy.com/project/badge/Coverage/801d031fd2714b4f9c643182f1fbbd0b\n   :target: https://www.codacy.com/app/adamcharnock/lightbus?utm_source=github.com&utm_medium=referral&utm_content=adamcharnock/lightbus&utm_campaign=Badge_Coverage\n   :alt: Codacy Badge\n\n\n.. image:: https://img.shields.io/discord/645218336229031946\n   :target: https://discord.gg/2j594ws\n   :alt: Discord\n\n\n.. image:: https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg\n   :target: https://lightbus.org/reference/code-of-conduct/\n   :alt: Contributor Covenant\n\n\nLightbus allows your backend processes to communicate, run background tasks,\nand expose internal APIs.\n\nLightbus uses Redis as its underlying transport, although support\nfor other platforms may eventually be added.\n\nLightbus requires Python 3.7 or above.\n\n**Full documentation can be found at https://lightbus.org**\n\nDesigned for ease of use\n------------------------\n\nLightbus is designed with developers in mind. The syntax aims to\nbe intuitive and familiar, and common problems are caught with\nclear and helpful error messages.\n\nFor example, a naïve authentication API:\n\n.. code-block:: python3\n\n   class AuthApi(Api):\n       user_registered = Event(parameters=('username', 'email'))\n\n       class Meta:\n           name = 'auth'\n\n       def check_password(self, user, password):\n           return (\n               user == 'admin'\n               and password == 'secret'\n           )\n\nThis can be called as follows:\n\n.. code-block:: python3\n\n   import lightbus\n\n   bus = lightbus.create()\n\n   bus.auth.check_password(\n       user='admin',\n       password='secret'\n   )\n   # Returns true\n\nYou can also listen for events:\n\n.. code-block:: python3\n\n   import lightbus\n\n   bus = lightbus.create()\n\n   def send_signup_email(event_message,\n                         username, email):\n       send_mail(email,\n           subject=f'Welcome {username}'\n       )\n\n   @bus.client.on_start()\n   def bus_start():\n       bus.auth.user_registered.listen(\n           send_signup_email\n       )\n\n**To get started checkout the documentation at https://lightbus.org.**\n",
    'author': 'Adam Charnock',
    'author_email': 'adam@adamcharnock.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://lightbus.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
