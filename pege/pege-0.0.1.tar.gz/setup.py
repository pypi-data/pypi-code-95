# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pege']

package_data = \
{'': ['*']}

install_requires = \
['egnn-pytorch>=0.2.6,<0.3.0',
 'pytorch-lightning>=1.4.7,<2.0.0',
 'torch>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'pege',
    'version': '0.0.1',
    'description': 'Protein embeddings to describe local electrostic enviroments',
    'long_description': '# Protein Enviroment Graph Embeddings (PEGE)\n\nProtein embeddings to describe local electrostic enviroments\n\n# Installation & Basic Usage\n\nPEG is installable from the Pypi repo:\n```bash\npython3 -m pip install peg\n```\n\nPeg can be used to obtain protein embeddings as well as descriptors for specific `atom_numbers` from a `pdb` file:\n```python\nfrom pege import Pege\n\nprotein = Pege(<pdb>)\nprotein_emb = protein.get_protein()\natoms_emb = protein.get_atoms([<atom_numbers>])\n```\n\n# Documentation\nTBA\n\n# License\nThis source code is licensed under the MIT license found in the LICENSE file in the root directory of this source tree.\n\n# Contacts\nPlease submit a github issue to report bugs and to request new features. Alternatively, you may email the developer [directly](mailto:pdreis@fc.ul.pt).\n\n',
    'author': 'Pedro Reis',
    'author_email': 'pdreis@fc.ul.pt',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bayer-science-for-a-better-life/pege',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2',
}


setup(**setup_kwargs)
