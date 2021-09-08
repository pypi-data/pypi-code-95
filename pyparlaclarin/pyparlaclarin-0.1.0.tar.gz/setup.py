# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['pyparlaclarin']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyparlaclarin',
    'version': '0.1.0',
    'description': 'Read, create, and modify Parla-Clarin XML files',
    'long_description': '# Pyparlaclarin\n\nThis module includes functionality for reading, creating, and modifying Parla-Clarin XML files.\n\nFor instance, you can loop over all paragraphs in a Parla-Clarin file with a simple function:\n\n```python\nfrom pyparlaclarin.read import paragraph_iterator\n\nfor paragraph in paragraph_iterator(root):\n\tprint(paragraph)\n```\n\nor get all speeches by a speaker\n\n```python\nfrom pyparlaclarin.read import speeches_with_name\n\nfor speech in speeches_with_name(root, name="barack_obama_1961"):\n\tprint(speech)\n```\n\nFurther documentation is available on [GitHub pages](https://welfare-state-analytics.github.io/pyparlaclarin/pyparlaclarin/).',
    'author': 'ninpnin',
    'author_email': 'vainoyrjanainen@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/welfare-state-analytics/pyparlaclarin',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
