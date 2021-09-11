# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['modpoll']

package_data = \
{'': ['*']}

install_requires = \
['paho-mqtt>=1.5.1,<2.0.0', 'pymodbus>=2.5.2,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0']}

entry_points = \
{'console_scripts': ['modpoll = modpoll:app']}

setup_kwargs = {
    'name': 'modpoll',
    'version': '0.2.9',
    'description': 'A command line tool to communicate with modbus devices',
    'long_description': '#modpoll\n\nA command line tool to poll modbus registers\n\n### Basic usages\n\n- Poll Modbus RTU device and save to local csv file\n```bash\nmodpoll --config examples/scpm-s6.csv --rtu /dev/ttyUSB0 --rtu-baud 9600 --export export.csv\n```\n- Poll Modbus TCP device and publish to MQTT broker\n```bash\nmodpoll --config examples/scpm-s6.csv --tcp 192.168.1.10 --tcp-port 502 --mqtt-host localhost\n```\n',
    'author': 'Ying Shaodong',
    'author_email': 'helloysd@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
