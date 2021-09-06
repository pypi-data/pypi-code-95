# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['glom_dict']

package_data = \
{'': ['*']}

install_requires = \
['glom>=20.11.0,<21.0.0']

setup_kwargs = {
    'name': 'glom-dict',
    'version': '0.0.1a0',
    'description': 'Custom Dictionary with glom get, set and del methods',
    'long_description': '# glom-dict\n\n[![ci](https://github.com/glom_dict/glom-dict/workflows/ci/badge.svg)](https://github.com/glom_dict/glom-dict/actions?query=workflow%3Aci)\n[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://glom_dict.github.io/glom-dict/)\n[![pypi version](https://img.shields.io/pypi/v/glom-dict.svg)](https://pypi.org/project/glom-dict/)\n\nCustom Dictionary with glom path compatible get, set and delete methods.\n\nhttps://glom.readthedocs.io/en/latest/\n\nFor easy access to and operations on nested data.\n\n## Installation\n\n```bash\npython -m pip install glom-dict\n```\n\n## Examples\n\n```python\n>>> from glom_dict import GlomDict\n>>> d = GlomDict(my_dict={"a": {"b": "c"}})\n>>> d["my_dict.a.b"]\n \'c\'\n\n>>> d["my_dict.a.b] = "C"\n>>> d["my_dict.a.b]\n \'C\'\n```\n\n### Better error messages.\n\n```python\n>>> d = GlomDict(**{\'a\': {\'b\': None}})\n>>> d["a.b.c"]\nTraceback (most recent call last):\n...\nPathAccessError: could not access \'c\', index 2 in path Path(\'a\', \'b\', \'c\'), got error: ...\n```\n\n### Glom Paths\n\n```python\nfrom glom_dict import GlomDict, Path\n>>> d = GlomDict({"a": {"b": ["works", "with", "lists", "too"]}})\n>>> d[Path("a", "b", 0)]\n\'works\'\n```\n\nFor more examples refer to the excellent `glom` tutorial.\n\nhttps://glom.readthedocs.io/en/latest/tutorial.html\n\n## Details\n\nBased on `collections.UserDict`\n\nImplemented methods\n\n- [x] `__getitem__` - `glom.glom()`\n- [x] `__setitem__` - `glom.assign()`\n- [x] `__delitem__` - `glom.delete()`\n- [ ] `update` - Works but no special behavior\n',
    'author': 'Gabriel',
    'author_email': 'gabriel59kg@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kilo59/glom-dict',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
