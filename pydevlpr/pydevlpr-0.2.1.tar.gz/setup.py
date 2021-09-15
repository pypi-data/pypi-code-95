# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pydevlpr']

package_data = \
{'': ['*']}

install_requires = \
['devlprd>=0.2.1,<0.3.0', 'pydevlpr-protocol>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'pydevlpr',
    'version': '0.2.1',
    'description': 'Frontend for connecting to devlprd and processing data from a FANTM DEVLPR',
    'long_description': '# pydevlpr\n\n## Overview\n\nEnables simple muscle to application connections. \nPydevlpr is the front-end for `devlprd <https://github.com/FANTM/devlprd>`_, and the third piece of the muscle-to-app pipeline.\n\n## Getting Started\n\nAfter installing pydevlpr, integrating it into a project is straightforward.\nFirst launch the `devlprd daemon <https://github.com/FANTM/devlprd>`_, and then use the ``add_callback(...)`` function to attach a handler to the incoming data.\nThe callback you attach will get the incoming payload as its only parameter, and then the data is yours to handle.\n\n## Supported Topics\n\nThis list will expand as the package matures, but when adding/removing callbacks use a data topic from this list as it maps directly to the daemon.\n\n* DataTopic.RAW_DATA_TOPIC - Data straight off the DEVLPR Arduino Shield. Range: 0-1023.\n* DataTopic.FLEX_TOPIC - 1 when there has been a flex, 0 when muscle is relaxed.\n\n## API\n\n*def stop() -> None:*\n\n> Stops listening to the server.\n\n*def add_callback(topic: str, pin: int, fn: Callable[[str], None], ws: websocket.server.WebSocketServerProtocol = None) -> None:*\n\n> Attaches a function to be called whenever a message is received at a particular topic and relating to a particular DEVLPR (as specified by the *pin* parameter).\n\n> - topic: str - Specifies the data stream, differentiating filtered vs. raw data.\n- pin: int - Connects the callback to a physical board. Each DEVLPR is connection to the Arduino via an analog pin, and the message from the daemon relates which pin this is.\n- fn: Callable[[str], None] - Function to be called when a message is received that is both the specified topic and pin. It expects to receive the payload of the incoming message.\n- ws: websocket.server.WebSocketServerProtocol - Websocket connection, by default set to None and uses pydevlprs global connection.\nPass a connection in if it is going to be used in another context, or for testing.\n\n*def remove_callback(topic: str, pin: int, fn: Callable[[str], None]) -> None:*\n\n> Stops a function from being called whenever a new qualified packet is received.\n\n> - topic: str - The data stream the existing callback is attached to.\n- pin: int - The DEVLPR the callback is attached to.\n- fn: Callable[[str], None] - Function to remove from the callback list.\n\n',
    'author': 'Ezra Boley',
    'author_email': 'hello@getfantm.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/FANTM/pydevlpr',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
