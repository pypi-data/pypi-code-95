# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xivapyi']

package_data = \
{'': ['*']}

modules = \
['py']
install_requires = \
['aiohttp>=3.7.4.post0,<4.0.0']

setup_kwargs = {
    'name': 'xivapyi',
    'version': '0.1.0',
    'description': 'An async python3 wrapper around the XIVAPI for Final Fantasy XIV.',
    'long_description': '# xivapyi\n\nAn async python3 wrapper around the XIVAPI for Final Fantasy XIV.\n\n## WARNING\n\nThis project is still in very early development, and will not be ready until the v1.0 release.\nPlease refrain from using xivapyi for now. Thanks for reading.\n\n## Installation\n\nxivapyi requires python 3.6 or greater.\n\nTo get started:\n```bash\npip install xivapyi\n```\n\n## Contributing\n\nThis library uses Poetry for dependency management. You can read more about it [here](https://python-poetry.org/docs/).\n\n## License\n\nxivapyi is licensed under the [BSD 3-Clause License](https://github.com/Jonxslays/xivapyi/blob/master/LICENSE).\n',
    'author': 'Jonxslays',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Jonxslays/xivapyi',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<=3.10',
}


setup(**setup_kwargs)
