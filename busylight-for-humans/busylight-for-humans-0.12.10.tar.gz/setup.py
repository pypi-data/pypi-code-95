# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['busylight',
 'busylight.api',
 'busylight.effects',
 'busylight.lights',
 'busylight.lights.agile_innovative',
 'busylight.lights.embrava',
 'busylight.lights.kuando',
 'busylight.lights.luxafor',
 'busylight.lights.plantronics',
 'busylight.lights.thingm']

package_data = \
{'': ['*']}

install_requires = \
['bitvector-for-humans>=0.14.0,<0.15.0',
 'hidapi>=0.9,<0.11',
 'loguru>=0.5.3,<0.6.0',
 'typer>=0,<1',
 'webcolors>=1.11.1,<2.0.0']

extras_require = \
{'webapi': ['uvicorn>=0.12.2,<0.16.0', 'fastapi>=0.61.1,<0.69.0']}

entry_points = \
{'console_scripts': ['busylight = busylight.main:cli']}

setup_kwargs = {
    'name': 'busylight-for-humans',
    'version': '0.12.10',
    'description': 'Control USB connected LED lights, like a human.',
    'long_description': '<!-- USB HID API embrava blynclight agile innovative blinkstick kuando busylight luxafor flag thingM blink(1) -->\n![BusyLight Project Logo][LOGO] <br>\n![supported python versions][python-versions]\n![version][pypi-version]\n![dependencies][dependencies]\n[![pytest][pytest-badge]][pytest-status]\n![license][license]\n![monthly-downloads][monthly-downloads]\n![Code style: black][code-style-black]\n\n\n[BusyLight for Humans™][0] gives you control of USB attached LED\nlights from a variety of vendors. Lights can be controlled via\nthe command-line, using a HTTP API or imported directly into your own\npython project.\n\n![All Supported Lights][DEMO]\n\n**Six Lights Attached to One Host**<br>\n<em>Back to Front, Left to Right</em> <br>\n<b>BlyncLight, BlyncLight Plus, Busylight</b> <br>\n<b>Blink(1), Flag, BlinkStick</b>\n\n## Features\n- Control lights from the [command-line][HELP].\n- Control lights via a [Web API][WEBAPI].\n- Import `busylight` into your own project.\n- Supports six vendors & multiple models:\n  * [**Agile Innovative** BlinkStick ][2]\n  * [**Embrava** Blynclight][3]\n  * [**Kuando** BusyLight][4]\n  * [**Luxafor** Flag][5]\n  * [**Plantronics** Status Indicator][3]\n  * [**ThingM** Blink1][6]\n- Supported on MacOS and Linux\n- Windows support will be available in the near future.\n\nIf you have a USB light that\'s not on this list open an issue\nwith the make and model device you want supported, where I can get\none, and any public hardware documentation you are aware of.\n\n### Gratitude\n\nThank you to [@todbot][todbot] and the very nice people at [ThingM][thingm] who\ngraciously and unexpectedly gifted me with two `blink(1) mk3` lights!\n\n## Basic Install\n\nInstalls only the command-line `busylight` tool and associated\nmodules.\n\n```console\n$ python3 -m pip install busylight-for-humans \n```\n\n## Web API Install\n\nInstalls `uvicorn` and `FastAPI` in addition to `busylight`:\n\n```console\n$ python3 -m pip install busylight-for-humans[webapi]\n```\n\n## Linux Post-Install Activities\n\nLinux controls access to USB devices via the [udev subsystem][UDEV]. By\ndefault it denies non-root users access to devices it doesn\'t\nrecognize. I\'ve got you covered!\n\nYou\'ll need root access to configure the udev rules:\n\n```console\n$ busylight udev-rules -o 99-busylights.rules\n$ sudo cp 99-busylights.rules /etc/udev/rules.d\n$ sudo udevadm control -R\n$ # unplug/plug your light\n$ busylight on\n```\n\n## Command-Line Examples\n\n```console\n$ busylight on               # light turns on green\n$ busylight on red           # now it\'s shining a friendly red\n$ busylight on 0xff0000      # still red\n$ busylight on #00ff00       # now it\'s blue!\n$ busylight blink            # it\'s slowly blinking on and off with a red color\n$ busylight blink green fast # blinking faster green and off\n$ busylight --all on         # turn all lights on green\n$ busylight --all off        # turn all lights off\n```\n\n## HTTP API Examples\n\nFirst start the `busylight` API server:\n```console\n$ busylight serve\nINFO:     Started server process [20189]\nINFO:     Waiting for application startup.\nINFO:     Application startup complete.\nINFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)\n```\n\nThe API is fully documented and available @ `https://localhost:8888/redoc`\n\n\nNow you can use the web API endpoints which return JSON payloads:\n\n```console\n  $ curl -s http://localhost:8888/lights\n  ...\n  $ curl -s http://localhost:8888/light/0/on | jq\n  {\n    "light_id": 0,\n    "action": "on",\n    "color": "green"\n  }\n  $ curl -s http://localhost:8888/light/0/off | jq\n  {\n    "light_id": 0,\n    "action": "off"\n  }\n  $ curl -s http://localhost:8888/light/0/on/purple | jq\n  {\n    "light_id": 0,\n    "action": "on",\n    "color": "purple"\n  }\n  $ curl -s http://localhost:8888/light/0/off | jq\n  {\n    "light_id": 0,\n    "action": "off"\n  }\n  $ curl -s http://localhost:8888/lights/on | jq\n  {\n    "light_id": "all",\n    "action": "on",\n    "color": "green"\n  }\n  $ curl -s http://localhost:8888/lights/off | jq\n  {\n    "light_id": "all",\n    "action": "off"\n  }\n  $ curl -s http://localhost:8888/lights/rainbow | jq\n  {\n    "light_id": "all",\n    "action": "effect",\n    "name": "rainbow"\n  }\n```\n\n### Authentication\nThe API can be secured with a simple username and password through\n[HTTP Basic Authentication][BASICAUTH]. To require authentication\nfor all API requests, set the `BUSYLIGHT_API_USER` and\n`BUSYLIGHT_API_PASS` environmental variables before running\n`busylight serve`.\n\n> :warning: **SECURITY WARNING**: HTTP Basic Auth sends usernames and passwords in *cleartext* (i.e., unencrypted). Use of SSL is highly recommended!\n\n## Code Examples\n\nAdding light support to your own python applications is easy!\n\n### Simple Case: Turn On a Single Light\n\nIn this example, we pick an Embrava Blynclight to activate with\nthe color white. \n\n```python\nfrom busylight.lights.embrava import Blynclight\n\nlight = Blynclight.first_light()\n\nlight.on((255, 255, 255))\n```\n\n### Slightly More Complicated\n\nThe `busylight` package includes a manager class that\'s great for\nworking with multiple lights or lights that require a little\nmore direct intervention like the Kuando Busylight series.\n\n```python\nfrom busylight.manager import LightManager, ALL_LIGHTS\nfrom busylight.effects import rainbow\n\nmanager = LightManager()\nfor light in manager.lights:\n   print(light.name)\n\nmanager.apply_effect_to_light(ALL_LIGHTS, rainbow)\n...\nmanager.lights_off(ALL_LIGHTS)\n```\n\n[0]: https://pypi.org/project/busylight-for-humans/\n\n<!-- doc links -->\n[2]: https://github.com/JnyJny/busylight/blob/master/docs/devices/agile_innovative.md\n[3]: https://github.com/JnyJny/busylight/blob/master/docs/devices/embrava.md\n[4]: https://github.com/JnyJny/busylight/blob/master/docs/devices/kuando.md\n[5]: https://github.com/JnyJny/busylight/blob/master/docs/devices/luxafor.md\n[6]: https://github.com/JnyJny/busylight/blob/master/docs/devices/thingm.md\n\n[LOGO]: https://github.com/JnyJny/busylight/blob/master/docs/assets/BusyLightLogo.png\n[HELP]: https://github.com/JnyJny/busylight/blob/master/docs/busylight.1.md\n[WEBAPI]: https://github.com/JnyJny/busylight/blob/master/docs/busylight_api.pdf\n[DEMO]: https://github.com/JnyJny/busylight/raw/master/demo/demo.gif\n\n[BASICAUTH]: https://en.wikipedia.org/wiki/Basic_access_authentication\n[UDEV]: https://en.wikipedia.org/wiki/Udev\n\n[todbot]: https://github.com/todbot\n[thingm]: https://thingm.com\n\n<!-- badges -->\n[pytest-badge]: https://github.com/JnyJny/busylight/actions/workflows/pytest.yaml/badge.svg\n[pytest-status]: https://github.com/JnyJny/busylight/actions/workflows/pytest.yaml\n[code-style-black]: https://img.shields.io/badge/code%20style-black-000000.svg\n[pypi-version]: https://img.shields.io/pypi/v/busylight-for-humans\n[python-versions]: https://img.shields.io/pypi/pyversions/busylight-for-humans\n[license]: https://img.shields.io/pypi/l/busylight-for-humans\n[dependencies]: https://img.shields.io/librariesio/github/JnyJny/busylight\n[monthly-downloads]: https://img.shields.io/pypi/dm/busylight-for-humans\n\n',
    'author': 'JnyJny',
    'author_email': 'erik.oshaughnessy@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/JnyJny/busylight.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
