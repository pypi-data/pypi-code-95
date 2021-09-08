# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyspare',
 'pyspare.deco',
 'pyspare.deco.deco_crostab',
 'pyspare.deco.deco_entries',
 'pyspare.deco.deco_json',
 'pyspare.deco.deco_matrix',
 'pyspare.deco.deco_node',
 'pyspare.deco.deco_node.helpers',
 'pyspare.deco.deco_node.preset',
 'pyspare.deco.deco_node.render',
 'pyspare.deco.deco_samples',
 'pyspare.deco.deco_str',
 'pyspare.deco.deco_table',
 'pyspare.deco.deco_vector',
 'pyspare.logger',
 'pyspare.logger.says',
 'pyspare.margin',
 'pyspare.margin.crostab_margin',
 'pyspare.margin.entries_margin',
 'pyspare.margin.matrix_margin',
 'pyspare.margin.table_margin',
 'pyspare.margin.utils',
 'pyspare.margin.vector_margin',
 'pyspare.padder',
 'pyspare.padder.crostab_padder',
 'pyspare.padder.entries_padder',
 'pyspare.padder.matrix_padder',
 'pyspare.padder.series_padder',
 'pyspare.padder.table_padder',
 'pyspare.padder.vector_padder']

package_data = \
{'': ['*']}

install_requires = \
['aryth>=0.0.12',
 'crostab>=0.0.5',
 'intype>=0.0.2',
 'ject>=0.0.3',
 'palett>=0.0.18',
 'texting>=0.0.9',
 'veho>=0.0.10']

setup_kwargs = {
    'name': 'pyspare',
    'version': '0.0.12',
    'description': 'pretty print',
    'long_description': '## pyspare\n##### pretty print\n\n### Usage\n```python\nfrom pyspare import deco\nvect = [1,2,3]\nprint(deco(vect))\n```',
    'author': 'Hoyeung Wong',
    'author_email': 'hoyeungw@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pydget/pyspare',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
