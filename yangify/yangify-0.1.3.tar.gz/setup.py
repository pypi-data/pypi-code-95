# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yangify',
 'yangify.linter',
 'yangify.model_filter',
 'yangify.parser',
 'yangify.translator']

package_data = \
{'': ['*']}

install_requires = \
['yangson==1.3.45']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.6.0,<0.7.0']}

setup_kwargs = {
    'name': 'yangify',
    'version': '0.1.3',
    'description': 'Library to help parsing/translating YANG models from/to native text/structures',
    'long_description': '# Yangify\n\nYangify is a framework that allows you to easily write code that can map structured and unstructured data into data modelled using YANG models. Yangify can also do the opposite operation and convert data modelled with YANG models into other structured or non-structured data. This allows you to easily write code that can parse native output/data/configuration from network devices and map them into YANG models and vice-versa.\n\n## Installing yangify\n\nYou can install yangify with pip:\n\n```\npip install yangify\n```\n\n## Ways to Get Started with Yangify\n\n\n* [Start Executing Juptyer Notebooks](#Start-Executing-Juptyer-Notebooks)\n* [Go Right into a Working Yangify Dev Environment](#Go-Right-into-a-Working-Yangify-Dev-Environment)\n* [Read the Docs](https://yangify.readthedocs.io)\n\n\n### Start Executing Yangify Juptyer Notebooks\n\n**Step 1**\n\nClone the repository:\n\n\n```\n$ git clone https://github.com/networktocode/yangify\n```\n\n\n**Step 2**\n\nNavigate into `yangify`:\n\n\n```\n$ cd yangify\n```\n\n\n**Step 3**\n\nBuild the containers needed.\n\n\n```\n$ make build_test_containers\n```\n\n**Step 4**\n\nStart a container so you can run Jupyter notebooks:\n\n\n```\nmake dev_jupyter\n```\n\n**Step 5**\n\nLaunch a browser and navigate to the following URL:\n\n```\nhttp://127.0.0.1:8888\n```\n\n\nYou will find all of the notebooks in `docs/tutorials` and also `docs/tutorials/parsing-quickstart`.\n\nThese same notebooks can be viewed without being interactive in the Read the Docs.\n\n\n\n### Go Right into a Working Yangify Dev Environment\n\n> Note: this dev environment is built for parsing.\n\n**Step 1**\n\nClone the repository:\n\n\n```\n$ git clone https://github.com/networktocode/yangify\n```\n\n\n**Step 2**\n\nNavigate into `yangify`:\n\n\n```\n$ cd yangify\n```\n\n\n**Step 3**\n\nBuild the containers needed.\n\n\n```\n$ make build_test_containers\n```\n\n\n**Step 4**\n\nCreate a container that you\'ll use for development & testing. This container will get built such that you can modify files in your local directory and execute them within the container environment.  Great for using your local text editor and executing in pre-buit enviornment.\n\n\n```\nmake enter_dev_container\n```\n\nThis will drop you right into the container.\n\n\n**Step 5**\n\nInstall `yangify` with `make install`:\n\n```\nroot@e726de8f2226:/yangify# make install\npoetry install\nSkipping virtualenv creation, as specified in config file.\nInstalling dependencies from lock file\n\nNothing to install or update\n\n  - Installing yangify (0.1.0)\nA setup.py file already exists. Using it.\nroot@e726de8f2226:/yangify#\n```\n\n\n**Step 6**\n\nNavigate into the `parsing-quickstart` directory (inside the container):\n\n\n```\nroot@e726de8f2226:/yangify# cd docs/tutorials/parsing-quickstart/\nroot@e726de8f2226:/yangify/docs/tutorials/parsing-quickstart#\n```\n\n**Step 7**\n\n\nTry out the `dev-yangify.py` script:\n\n\n```\nroot@e726de8f2226:/yangify/docs/tutorials/parsing-quickstart# python dev-yangify.py --vlans\n{\n    "openconfig-vlan:vlans": {\n        "vlan": [\n            {\n                "vlan-id": 10,\n                "config": {\n                    "vlan-id": 10,\n                    "status": "ACTIVE"\n                }\n            },\n            {\n                "vlan-id": 20,\n                "config": {\n                    "vlan-id": 20,\n                    "name": "web_vlan",\n                    "status": "ACTIVE"\n                }\n            },\n            {\n                "vlan-id": 30,\n                "config": {\n                    "vlan-id": 30,\n                    "name": "test_vlan",\n                    "status": "ACTIVE"\n                }\n            }\n        ]\n    }\n}\nroot@e726de8f2226:/yangify/docs/tutorials/parsing-quickstart#\n```\n',
    'author': 'David Barroso',
    'author_email': 'dbarrosop@dravetech.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
