# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lemmy', 'lemmy.cli', 'lemmy.pipe']

package_data = \
{'': ['*']}

install_requires = \
['conllu>=4.4.1,<5.0.0',
 'spacy>=3.1.0,<4.0.0',
 'srsly>=2.4.1,<3.0.0',
 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['lemmy = lemmy.cli.__main__:app']}

setup_kwargs = {
    'name': 'lemmy3',
    'version': '3.0.0a0',
    'description': 'Lemmy lemmatizer',
    'long_description': '# 🤘 Lemmy3\n\nLemmy3 is an experimental fork of [Lemmy](https://github.com/sorenlind/lemmy)\n\nIt has been refactored in object-oriented manner, the codebase is extended with type-hints and spacy-compatible serialization, and a simple frequency-based disambiguation method is added. The tool comes with a command line interface (`lemmy`) for training lemmatizer models.',
    'author': 'Gyorgy Orosz',
    'author_email': 'gyorgy@orosz.link',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/spacy-hu/lemmy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
