# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aioswitcher', 'aioswitcher.api', 'aioswitcher.device', 'aioswitcher.schedule']

package_data = \
{'': ['*']}

extras_require = \
{'docs': ['insegel==1.2.0',
          'sphinx==4.1.2',
          'sphinxcontrib-autoprogram==0.1.7',
          'sphinxcontrib-spelling==7.2.1',
          'toml==0.10.2']}

setup_kwargs = {
    'name': 'aioswitcher',
    'version': '2.0.5',
    'description': 'Switcher Python Integration.',
    'long_description': '# Switcher Python Integration</br>[![pypi-version]][11] [![pypi-downloads]][11] [![license-badge]][4]\n\n[![gh-build-status]][7] [![gh-pages-status]][8] [![codecov]][3]\n\nPyPi module integrating with various [Switcher][12] devices.</br>\nCheck out the [wiki pages][0] for a list of supported devices.\n\n## Install\n\n```shell\npip install aioswitcher\n```\n\n## Usage Example\n\n```python\nasync with SwitcherApi(device_ip, device_id) as swapi:\n    # get the device state\n    state_response = await swapi.get_state()\n\n    # control the device on for 15 minutes and then turn it off\n    await swapi.control_device(Command.ON, 15)\n    await swapi.control_device(Command.OFF)\n\n    # create a new recurring schedule\n    await swapi.create_schedule("13:00", "14:30", {Days.SUNDAY, Days.FRIDAY})\n```\n\nCheck out the [documentation][8] for a more detailed usage section.\n\n## Command Line Helper Scripts\n\n- [discover_devices.py](scripts/discover_devices.py) can discover devices and their\n  states.\n- [control_device.py](scripts/control_device.py) can to control a device.\n\n## Contributing\n\nThe contributing guidelines are [here](.github/CONTRIBUTING.md)\n\n## Code of Conduct\n\nThe code of conduct is [here](.github/CODE_OF_CONDUCT.md)\n\n## Thanks\n\n- Preliminary work done by [Shai][13] and Aviad in [Switcher-V2-Python][14].\n- Research and help for advancing and adding features by [Shay][15].\n- Cooperation and general support by the people at [Switcher][12].\n\n## Disclaimer\n\nThis is **NOT** an official module and it is **NOT** officially supported by the vendor.\n\n<!-- Real Links -->\n[0]: https://github.com/TomerFi/aioswitcher/wiki\n[2]: https://github.com/TomerFi/aioswitcher/releases\n[3]: https://codecov.io/gh/TomerFi/aioswitcher\n[4]: https://github.com/TomerFi/aioswitcher\n[7]: https://github.com/TomerFi/aioswitcher/actions/workflows/pre_release.yml\n[8]: https://aioswitcher.tomfi.info/\n[11]: https://pypi.org/project/aioswitcher\n[12]: https://www.switcher.co.il/\n[13]: https://github.com/NightRang3r\n[14]: https://github.com/NightRang3r/Switcher-V2-Python\n[15]: https://github.com/thecode\n<!-- Badges Links -->\n[codecov]: https://codecov.io/gh/TomerFi/aioswitcher/graph/badge.svg\n[gh-build-status]: https://github.com/TomerFi/aioswitcher/actions/workflows/pre_release.yml/badge.svg\n[gh-pages-status]: https://github.com/TomerFi/aioswitcher/actions/workflows/pages_deploy.yml/badge.svg\n[license-badge]: https://img.shields.io/github/license/tomerfi/aioswitcher\n[pypi-downloads]: https://img.shields.io/pypi/dm/aioswitcher.svg?logo=pypi&color=1082C2\n[pypi-version]: https://img.shields.io/pypi/v/aioswitcher?logo=pypi\n',
    'author': 'Tomer Figenblat',
    'author_email': 'tomer.figenblat@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/aioswitcher/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
