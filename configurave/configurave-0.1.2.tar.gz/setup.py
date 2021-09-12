# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['configurave']
install_requires = \
['atoml>=1.0.3,<2.0.0']

extras_require = \
{'dotenv': ['python-dotenv>=0.19.0,<0.20.0']}

setup_kwargs = {
    'name': 'configurave',
    'version': '0.1.2',
    'description': 'A one-size-fits-all configuration scheme manager',
    'long_description': '# Configurave\n[![Lint & Test](https://img.shields.io/github/workflow/status/discord-modmail/configurave/Lint%20&%20Test/main?label=Lint+%26+Test&logo=github&style=flat)](https://github.com/discord-modmail/configurave/actions/workflows/lint_test.yml "Lint and Test")\n[![Python](https://img.shields.io/static/v1?label=Python&message=3.7+|+3.8+|+3.9&color=blue&logo=Python&style=flat)](https://www.python.org/downloads/ "Python 3.7 | 3.8 | 3.9")\n[![Code Style](https://img.shields.io/static/v1?label=Code%20Style&message=black&color=000000&style=flat)](https://github.com/psf/black "The uncompromising python formatter")\n\n\nConfigurave is a one-stop configuration engine that permits writing your configuration as a simple decorated class, and then loading the values from a series of configuration files or providers.\n\nValues loaded from later sources override values provided by earlier sources. Types of the loaded configuration values are checked.\n\nWhile not currently functional, there are plans and code to write out a default configuration generated directly from the configurave decorated class with .defaults_toml().\n\nThis project has undergone _MINIMAL_ testing and work. It is likely very buggy at this time. Stay tuned for more!\n\nExample usage:\n\n```py\nfrom typing import List\n\nfrom configurave import make_config, ConfigEntry as ce\n\n@make_config()\nclass MyConfig:\n    site_root: str = ce(comment="The root url the site should be mounted on")\n    template_root: str = ce(comment="Directory under which templates should be found")\n    allowed_hosts: List[str] = ce(\n        comment="A comma separated list of hosts that we are permitted to server content to",\n        validator=lambda config, value: len(value) > 0,\n    )\n    token: str = ce(comment="The discord auth token", secret=True)\n\nconfig = MyConfig(sources=["tests/test-config/readme.toml"])\n\nprint(config.site_root, config.template_root, config.allowed_hosts[0], sep="\\n")\n\n```\n\nThis will load from a file that looks like:\n```toml\ntemplate_root = "./templates"\nallowed_hosts = "mydomain.com,example.example,localhost:8080"\n\n[site]\nroot = "/"\n```\n\nor\n\n```env\nTEMPLATE_ROOT="./templates"\nALLOWED_HOSTS="mydomain.com,example.example,localhost:8080"\nSITE_ROOT="/"\n```\n\nand print:\n```\n/\n./templates\n["mydomain.com", "example.example", "localhost:8080"]\n```\n',
    'author': 'Bast',
    'author_email': 'bast@fastmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/discord-modmail/configurave',
    'py_modules': modules,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
