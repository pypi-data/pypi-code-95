# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ossindex']

package_data = \
{'': ['*']}

install_requires = \
['packageurl-python>=0.9.4,<0.10.0',
 'requests>=2.26.0,<3.0.0',
 'tinydb>=4.5.1,<5.0.0']

setup_kwargs = {
    'name': 'ossindex-lib',
    'version': '0.2.1',
    'description': 'A library for querying the OSS Index free catalogue of open source components to help developers identify vulnerabilities, understand risk, and keep their software safe.',
    'long_description': '# Python Library for quering OSS Index\n\n![GitHub Workflow Status](https://img.shields.io/github/workflow/status/sonatype-nexus-community/ossindex-python/Python%20CI)\n![Python Version Support](https://img.shields.io/badge/python-3.6+-blue)\n![PyPI Version](https://img.shields.io/pypi/v/ossindex-lib?label=PyPI&logo=pypi)\n[![GitHub license](https://img.shields.io/github/license/sonatype-nexus-community/ossindex-python)](https://github.com/sonatype-nexus-community/ossindex-python/blob/main/LICENSE)\n[![GitHub issues](https://img.shields.io/github/issues/sonatype-nexus-community/ossindex-python)](https://github.com/sonatype-nexus-community/ossindex-python/issues)\n[![GitHub forks](https://img.shields.io/github/forks/sonatype-nexus-community/ossindex-python)](https://github.com/sonatype-nexus-community/ossindex-python/network)\n[![GitHub stars](https://img.shields.io/github/stars/sonatype-nexus-community/ossindex-python)](https://github.com/sonatype-nexus-community/ossindex-python/stargazers)\n\n----\n\nThis OSSIndex module for Python provides a common interface to querying the [OSS Index](https://ossindex.sonatype.org/).\n\nThis module is not designed for standalone use. If you\'re looking for a tool that can detect your application\'s dependencies\nand assess them for vulnerabilities against the OSS Index, perhaps you should check out \n[Jake](https://github.com/sonatype-nexus-community/jake).\n\nYou can of course use this library in your own applications.\n\n## Installation\n\nInstall from pypi.org as you would any other Python module:\n\n```\npip install ossindex-lib\n```\n\n## Usage\n\nFirst create an instance of `OssIndex`, optionally enabling local caching\n```\no = OssIndex()\n```\n\nThen supply a `List` of [PackageURL](https://github.com/package-url/packageurl-python) objects that you want to ask\nOSS Index about. If you don\'t want to care about generating this list yourself, perhaps look to a tool like [Jake](https://github.com/sonatype-nexus-community/jake)\n(which uses this library) and will do all the hard work for you!\n\nAs a quick test, you could run:\n```\no = OssIndex()\nresults: List[OssIndexComponent] = o.get_component_report(packages=[\n    PackageURL.from_string(purl=\'pkg:pypi/pip@19.2.0\')\n])\nfor r in results:\n    print("{}: {} known vulnerabilities".format(r.get_coordinates(), len(r.get_vulnerabilities())))\n    v: Vulnerability\n    for v in r.get_vulnerabilities():\n        print(\'    - {}\'.format(str(v)))\n```\n\n... which would output something like ...\n```\npkg:pypi/pip@19.2.0: 1 known vulnerabilities\n    - <Vulnerability id=e4c955a3-2004-472e-920b-783fea46c3cd, name=OSSINDEX-783f-ea46-c3cd, cvss_score=3.6>\n```\n\n## Logging\n\nThis library send log events to a standard Python `logger` named `ossindex`. You can configure the logger to output as\nrequired through the standard [Python logging configuration](https://docs.python.org/3/library/logging.config.html).\n\n## Todos\n\n1. Support authentication against OSS Index\n\n## Python Support\n\nWe endeavour to support all functionality for all [current actively supported Python versions](https://www.python.org/downloads/).\nHowever, some features may not be possible/present in older Python versions due to their lack of support.\n\n## Changelog\n\nSee our [CHANGELOG](./CHANGELOG.md).\n\n## The Fine Print\n\nRemember:\n\nIt is worth noting that this is **NOT SUPPORTED** by Sonatype, and is a contribution of ours to the open source\ncommunity (read: you!)\n\n* Use this contribution at the risk tolerance that you have\n* Do NOT file Sonatype support tickets related to `ossindex-lib`\n* DO file issues here on GitHub, so that the community can pitch in\n\nPhew, that was easier than I thought. Last but not least of all - have fun!\n',
    'author': 'Paul Horton',
    'author_email': 'phorton@sonatype.com',
    'maintainer': 'Paul Horton',
    'maintainer_email': 'phorton@sonatype.com',
    'url': 'https://github.com/sonatype-nexus-community/ossindex-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
