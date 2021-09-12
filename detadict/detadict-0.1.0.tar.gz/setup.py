# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['detadict']

package_data = \
{'': ['*']}

install_requires = \
['deta>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'detadict',
    'version': '0.1.0',
    'description': 'Python dict with Deta backend',
    'long_description': '# detadict\n\n__Goal:__ create dictionary that fully compatible with native python dictionary interface.\n\n__Example:__\n```python\nfrom detadict import detadict\n\nusers = detadict()\nusers["John"] = {\n  "id": 1,\n  "sex": "male"\n}\nusers["Katy"] = {\n  "id": 2,\n  "sex": "female"\n}\n```\n\n__Requirements:__\n\n🤦\u200d♂️ All you need to do is set the environment variable `DETA_PROJECT_KEY` with the Deta project key.\n\n__Currently not supported__:\n\n- Update of mutable values\n\n```python\nusers["John"]["sex"] = "female"\nprint(users["John"])  # {"id": 1, "sex": "male"}\n```\n\n- `copy` and `setdefault` methods\n\n```python\n# raise NotImplementedError\nusers.copy()\nusers.setdefault("Bob", {})\n```\n\n__Installing__:\n```bash\npip install detadict\n```\n',
    'author': 'ilhomidin',
    'author_email': 'itilhomidin@yandex.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ilhomidin/detadict',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
