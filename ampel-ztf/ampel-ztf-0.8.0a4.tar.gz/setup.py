# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ampel',
 'ampel.template',
 'ampel.util',
 'ampel.ztf',
 'ampel.ztf.alert',
 'ampel.ztf.base',
 'ampel.ztf.dev',
 'ampel.ztf.ingest',
 'ampel.ztf.t0',
 'ampel.ztf.t0.load',
 'ampel.ztf.t1',
 'ampel.ztf.t2',
 'ampel.ztf.t3',
 'ampel.ztf.t3.complement',
 'ampel.ztf.t3.select',
 'ampel.ztf.t3.skyportal',
 'ampel.ztf.util']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.3,<4.0.0',
 'ampel-alerts>=0.8.0-alpha.2,<0.9.0',
 'ampel-core>=0.8.0-alpha.4,<0.9.0',
 'ampel-interface>=0.8.0-alpha.0,<0.9.0',
 'ampel-photometry>=0.8.0-alpha.0,<0.9.0',
 'astropy>=4.2,<5.0',
 'backoff>=1.10.0,<2.0.0',
 'confluent-kafka>=1.5.0,<2.0.0',
 'fastavro>=1.3.2,<2.0.0',
 'matplotlib>=3.3.4,<4.0.0',
 'nest-asyncio>=1.4.3,<2.0.0',
 'requests-toolbelt>=0.9.1,<0.10.0',
 'requests>=2.25.1,<3.0.0']

extras_require = \
{'archive': ['ampel-ztf-archive>=0.8.0-alpha.0,<0.9.0'],
 'light-curve': ['light-curve-python>=0.2.5,<0.4.0']}

setup_kwargs = {
    'name': 'ampel-ztf',
    'version': '0.8.0a4',
    'description': 'Zwicky Transient Facility support for the Ampel system',
    'long_description': '\n\n<img align="left" src="https://desycloud.desy.de/index.php/s/6gJs9bYBG3tWFDz/preview" width="150" height="150"/>  \n<br>\n\n# ZTF support for AMPEL\n\n<br><br>\nZTF-specific implementations for Ampel such as:\n\n- An _AlertSupplier_ compatible with IPAC generated alerts\n- Shaper classes for ingestion\n- Encoding utilities for ZTF names (AMPEL requires integer ids)\n- Classes for archiving alerts\n',
    'author': 'Valery Brinnel',
    'author_email': None,
    'maintainer': 'Jakob van Santen',
    'maintainer_email': 'jakob.van.santen@desy.de',
    'url': 'https://ampelproject.github.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
