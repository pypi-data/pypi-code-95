# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['devlprd']

package_data = \
{'': ['*']}

install_requires = \
['mypy>=0.910,<0.911',
 'pydevlpr-protocol>=0.1.0,<0.2.0',
 'pyserial>=3.5,<4.0',
 'websockets>=9.1,<10.0']

setup_kwargs = {
    'name': 'devlprd',
    'version': '0.2.1',
    'description': 'Daemon for managing integrations with the FATNM DEVLPR',
    'long_description': "# devlprd\n[![Python application](https://github.com/FANTM/devlprd/actions/workflows/python-app.yml/badge.svg)](https://github.com/FANTM/devlprd/actions/workflows/python-app.yml)\n\n## Overview\nThe FANTM DEVLPR daemon for managing and publishing data streams. It serves as a middleware between the hardware itself, and whatever integration you want to make. \nIt exists to both abstract away data processing from the end application, and to allow for language agnostic integrations. Right now there is only a [python endpoint](https://github.com/FANTM/pydevlpr), but there are plans for JS and more in the near future. \nIn effect, first an Arduino is flashed with the provided firmware, then the daemon is launched, and then the application that you're using the data with. \n\n## Getting Started\nThe first thing that needs to be done is formatting the Arduino. In the `arduino_firmware` folder there are scripts that format the data in such a way that the daemon can package, process, and send it out easily. \nSo [flash an arduino](https://www.arduino.cc/en/Guide) with one of those scripts and make sure it is connected to the computer you will be running the daemon from.\n\nThis project uses [Poetry](https://python-poetry.org/) for dependency management, and while it's not required to get started it's a useful tool. All of the dependencies are in `pyproject.toml`,\nso just run `poetry install`. Then just run `poetry run python src/main.py` and the daemon should start.\n\n## Development\n### Adding a data transformer\nTo add support for a new data transformer, edit the `self.callbacks: Dict[str, Callable[[int], Union[int, bool]]]` dictionary in the `__init__` function of DaemonState (in `DaemonState.py`).\nYou will need to add a new entry with a data topic, using one of the supported topics defined in `protocol.py` and a function. \nThe function is a callback that takes a single int as an arguement representing the pin the data is coming from on the Arduino.\nThe function should be inside of DaemonState, but it can be wrapper for a function living in another file (`filtering.py` is usually a good choice). \n\nNow whenever a client subscribes to your topic, the callback will be called and you'll see your data stream.\n\n### Adding a new data topic\nAdd a new line to the DataTopic class in `protocol.py` with an ALL_CAPS_NAME and a unique two letter identifier. \nThen go to the [`protocol.py`](https://github.com/FANTM/pydevlpr/blob/main/src/pydevlpr/protocol.py) in the `pydevlpr` repository and add it there as well so others can use the topic. \n\n### Adding support for different types of messages\nAdd a new line in the PacketType class in `protocol.py` with an ALL_CAPS_NAME and a unique one letter identifier. \nThen go to `daemon.py` and add an `elif command == PacketType.ALL_CAPS_NAME` with the handler for your custom packet type to the `receive(...)` function.\n",
    'author': 'Ezra Boley',
    'author_email': 'eboley@wisc.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/FANTM/devlprd',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
