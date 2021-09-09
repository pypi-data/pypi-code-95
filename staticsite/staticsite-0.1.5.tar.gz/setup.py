# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['staticsite']

package_data = \
{'': ['*']}

install_requires = \
['Flask-Minify>=0.23,<0.24', 'Jinja2>=2.11.2,<3.0.0', 'pyyaml>=5.3.1,<6.0.0']

setup_kwargs = {
    'name': 'staticsite',
    'version': '0.1.5',
    'description': 'Super simple Jinja2 based staticsite generator.',
    'long_description': '# StaticSite\n\n- [Documentation](https://thesage21.github.io/staticsite/)\n- See examples folder for ways to do common things.\n- Usage\n  1. Create a folder called `src`.\n  2. Put your Jinja templates there.\n  3. Run `python -m staticsite build --src src --target www`\n  4. Static site has been built and provided in `www` folder.\n  5. Create a `staticsite.yaml` file to specify variables and plugins.\n',
    'author': 'arjoonn sharma',
    'author_email': 'arjoonn.94@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://thesage21.github.io/staticsite/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
