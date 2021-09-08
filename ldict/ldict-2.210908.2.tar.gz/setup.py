# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ldict']

package_data = \
{'': ['*']}

install_requires = \
['garoupa>=2.210907.7,<3.0.0',
 'orjson>=3.5.0,<4.0.0',
 'pdoc3>=0.10.0,<0.11.0',
 'uncompyle6>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'ldict',
    'version': '2.210908.2',
    'description': 'Lazy dict with universally unique identifier for values',
    'long_description': '![test](https://github.com/davips/ldict/workflows/test/badge.svg)\n[![codecov](https://codecov.io/gh/davips/ldict/branch/main/graph/badge.svg)](https://codecov.io/gh/davips/ldict)\n\n# ldict\nUniquely identified lazy dict.\n\n[Latest version](https://github.com/davips/ldict)\n\n## Installation\n### as a standalone lib.\n```bash\n# Set up a virtualenv. \npython3 -m venv venv\nsource venv/bin/activate\n\n# Install from PyPI...\npip install --upgrade pip\npip install -U ldict\n\n# ...or, install from updated source code.\npip install git+https://github.com/davips/ldict\n```\n\n### from source\n```bash\ngit clone https://github.com/davips/ldict\ncd ldict\npoetry install\n```\n\n## Examples\n**Merging two ldicts**\n<details>\n<p>\n\n```python3\nfrom ldict import ldict\n\na = ldict(x=3)\nprint(a)\n"""\n{\n    "id": "kr_4aee5c3bcac2c478be9901d57fd1ef8a9d002",\n    "ids": "kr_4aee5c3bcac2c478be9901d57fd1ef8a9d002",\n    "x": 3\n}\n"""\n```\n\n```python3\n\nb = ldict(y=5)\nprint(b)\n"""\n{\n    "id": "Uz_0af6d78f77734fad67e6de7cdba3ea368aae4",\n    "ids": "Uz_0af6d78f77734fad67e6de7cdba3ea368aae4",\n    "y": 5\n}\n"""\n```\n\n```python3\n\nprint(a >> b)\n"""\n{\n    "id": "c._2b0434ca422114262680df425b85cac028be6",\n    "ids": "kr_4aee5c3bcac2c478be9901d57fd1ef8a9d002 Uz_0af6d78f77734fad67e6de7cdba3ea368aae4",\n    "x": 3,\n    "y": 5\n}\n"""\n```\n\n\n</p>\n</details>\n\n## Features (current or planned)\n* [x] \n* [ ] \n\n## Persistence\n`poetry install -E full`\n\n## Concept\nA ldict is like a common Python dict, with extra funtionality.\nIt is a mapping between string keys, called fields, and any serializable object.\nThe ldict `id` (identifier) and the field `ids` are also part of the mapping.  \n\nThe user can provide a unique identifier ([hosh](https://pypi.org/project/garoupa))\nfor each function or value object.\nOtherwise, they will be calculated through blake3 hashing of the content of data or bytecode of function.\nFor this reason, such functions should be simple, i.e.,\nwith minimal external dependencies, to avoid the unfortunate situation where two\nfunctions with identical local code actually perform different calculations through\ncalls to external code that implement different algorithms with the same name.\nAlternatively, a Hosh object can be passed inside the dict that is returned by the function, under the key "_id".\n\n## How to use\n[ongoing...]\n',
    'author': 'davips',
    'author_email': 'dpsabc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
