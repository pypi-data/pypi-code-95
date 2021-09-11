# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scrapysplashwrapper']

package_data = \
{'': ['*']}

install_requires = \
['Scrapy>=2.5.0,<3.0.0', 'scrapy-splash>=0.7.2,<0.8.0']

extras_require = \
{'docs': ['Sphinx>=4.1.2,<5.0.0']}

entry_points = \
{'console_scripts': ['scraper = scrapysplashwrapper:main']}

setup_kwargs = {
    'name': 'scrapysplashwrapper',
    'version': '1.8.1',
    'description': 'Scrapy splash wrapper as a standalone library.',
    'long_description': '[![Documentation Status](https://readthedocs.org/projects/scrapysplashwrapper/badge/?version=latest)](https://scrapysplashwrapper.readthedocs.io/en/latest/?badge=latest)\n\n# ScrapySplashWrapper\nA wrapper that uses scrappy and splash to crawl a website.\n\n# Usage\n\n*Warning*: it requires a splash instance (docker is recommendended).\n\n```\nusage: scraper [-h] [-s SPLASH] -u URL [-d DEPTH] [-o OUTPUT] [-ua USERAGENT]\n               [--debug]\n\nCrawl a URL.\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -s SPLASH, --splash SPLASH\n                        Splash URL to use for crawling.\n  -u URL, --url URL     URL to crawl\n  -d DEPTH, --depth DEPTH\n                        Depth of the crawl.\n  -o OUTPUT, --output OUTPUT\n                        Output directory\n  -ua USERAGENT, --useragent USERAGENT\n                        User-Agent to use for crawling\n  --debug               Enable debug mode on scrapy/splash\n\n```\n\n',
    'author': 'Raphaël Vinot',
    'author_email': 'raphael.vinot@circl.lu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Lookyloo/ScrapySplashWrapper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
