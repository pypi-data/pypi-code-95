# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rashsetup',
 'rashsetup.RashScrappers',
 'rashsetup.RashScrappers.RashScrappers',
 'rashsetup.RashScrappers.RashScrappers.spiders',
 'rashsetup.__RashModules__',
 'rashsetup.__RashModules__.Rash',
 'rashsetup.__RashModules__.Rash.Bars',
 'rashsetup.__RashModules__.Rash.Bars.Docks',
 'rashsetup.__RashModules__.Rash.Bars.Menu',
 'rashsetup.__RashModules__.Rash.Bars.Status',
 'rashsetup.__RashModules__.Rash.Bars.TabBar',
 'rashsetup.__RashModules__.Rash.Bars.Tools',
 'rashsetup.__RashModules__.Rash.Bars.Tools.RashLogger',
 'rashsetup.__RashModules__.Rash.Home',
 'rashsetup.__RashModules__.Rash.MainWindow',
 'rashsetup.__RashModules__.Rash.Processes',
 'rashsetup.__RashModules__.Rash.Source',
 'rashsetup.__RashModules__.Rash.Source.Manager',
 'rashsetup.__RashModules__.SimpleP']

package_data = \
{'': ['*'],
 'rashsetup.__RashModules__': ['Rash/Misc/CSS/*',
                               'Rash/Misc/Cache/*',
                               'Rash/Misc/HTML/*',
                               'Rash/Misc/HTML/TextBrowser/*',
                               'Rash/Misc/HTML/WebEngineView/*',
                               'Rash/Misc/Non_Cache/*',
                               'Rash/Misc/Non_Cache/Fonts/*']}

install_requires = \
['Scrapy>=2.5.0,<3.0.0']

setup_kwargs = {
    'name': 'rashsetup',
    'version': '0.6.3',
    'description': 'Setup Module that can be used for both testing Rash and also Setting up Rash',
    'long_description': None,
    'author': 'Rahul',
    'author_email': 'saihanumarahul66@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<3.10',
}


setup(**setup_kwargs)
