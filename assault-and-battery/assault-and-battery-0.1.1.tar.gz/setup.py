# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['assault_and_battery']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.3,<4.0.0', 'pyserial>=3.5,<4.0']

entry_points = \
{'console_scripts': ['assault = assault_and_battery.cli:cli']}

setup_kwargs = {
    'name': 'assault-and-battery',
    'version': '0.1.1',
    'description': 'A battery discharge curve calculator slash torture test.',
    'long_description': "# Battery discharge calculator\n\nThis is a simple script that will calculate the discharge curve of a battery. It does\nthis by communicating with a flight controller running INAV (with calibrated voltage and\ncurrent sensors) with a constant load attached.\n\nIt reads the voltage, instant amperage, and Ah consumed, and writes the samples to a CSV\nfile for later plotting.\n\n\n## Installation\n\nUse pipx:\n\n```bash\n$ pipx install assault_and_battery\n```\n\nAnd run the script as:\n\n```bash\n$ assault --help\n```\n\n## Usage\n\nPlug an FC with calibrated sensors to USB, making sure to either cut the VCC cable (or\nput some tape over the VCC pin), or use Bluetooth, USB-Serial, or some other way that\ndoesn't power the FC. Also make sure to not have any ground loops.\n\nThen, run the script and start your load. It will output a CSV file with the current\ndate and all the measurements.\n\nTo plot stuff, use `assault plot <csv file>`. You can delete the first few values if the\nload hasn't ramped up, or if you want to get rid of starting noise. This will produce\na graph, that's about it.\n",
    'author': 'Stavros Korokithakis',
    'author_email': 'hi@stavros.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/stavros/assault-and-battery/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
