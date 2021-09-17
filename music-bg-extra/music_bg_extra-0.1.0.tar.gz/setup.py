# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['music_bg_extra', 'music_bg_extra.processors', 'music_bg_extra.variables']

package_data = \
{'': ['*']}

install_requires = \
['Pillow-SIMD>=7.0.0,<8.0.0']

entry_points = \
{'mbg_processors': ['box_blur = music_bg_extra.processors.blur:box_blur',
                    'circle = music_bg_extra.processors.circle:circle',
                    'gaussian_blur = '
                    'music_bg_extra.processors.blur:gaussian_blur'],
 'mbg_variables': ['uuid4 = music_bg_extra.variables.uuid_gen:uuid4']}

setup_kwargs = {
    'name': 'music-bg-extra',
    'version': '0.1.0',
    'description': 'Extra utils for music_bg',
    'long_description': '# Extra processors and variables for music_bg.\n\nThis is a plugin for [music_bg](https://github.com/music-bg/music_bg) package.\n\n## Plugin contents\n\nProcessors:\n* Box blur;\n* Gaussian blur;\n* Circle;\n\nVariables:\n* uuid4\n\n## Variables\n\nYou can use "uuid4" or "{uuid4.hex}" in your config to generate\nUUIDv4.\n\n\n## Processors\n\nTo blur an image add this to your layer config:\n```json\n{\n    "name": "box_blur",\n    "args": {\n        "strength": "6"\n    }\n}\n```\nOr you can use gaussian blur.\nAs an optional parameter you\ncan adjust radius.\n```json\n{\n    "name": "gaussian_blur",\n    "args": {\n        "radius": "5.4"\n    }\n}\n```\n\n### Circle processor\nThis processor will crop a circle\nout of an image.\nTo use it add this to your conig file:\n```\n{\n    "name": "circle"\n}\n```\n\nIt doesn\'t take any args.\n',
    'author': 'Pavel Kirilin',
    'author_email': 'win10@list.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
