# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cyclonedx_py']

package_data = \
{'': ['*']}

install_requires = \
['cyclonedx-python-lib>=0.0.10,<0.0.11']

entry_points = \
{'console_scripts': ['cyclonedx-py = cyclonedx_py.client:main']}

setup_kwargs = {
    'name': 'cyclonedx-bom',
    'version': '1.0.2',
    'description': 'CycloneDX Software Bill of Materials (SBOM) generation utility',
    'long_description': "# CycloneDX Python SBOM Generation Tool\n\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/CycloneDX/cyclonedx-python/Python%20CI)](https://github.com/CycloneDX/cyclonedx-python/actions/workflows/ci.yml)\n[![Docker Image](https://img.shields.io/badge/docker-image-brightgreen?style=flat&logo=docker)](https://hub.docker.com/r/cyclonedx/cyclonedx-python)\n[![GitHub license](https://img.shields.io/github/license/CycloneDX/cyclonedx-python)](https://github.com/CycloneDX/CycloneDX/blob/main/LICENSE)\n[![Python Version Support](https://img.shields.io/badge/https://-cyclonedx.org-blue)](https://cyclonedx.org/)\n[![Slack Invite](https://img.shields.io/badge/Slack-Join-blue?logo=slack&labelColor=393939)](https://cyclonedx.org/slack/invite)\n![PyPI Version](https://img.shields.io/pypi/v/cyclonedx-bom?label=PyPI&logo=pypi)\n![Python Version Support](https://img.shields.io/badge/python-3.6+-blue)\n[![Group Discussion](https://img.shields.io/badge/discussion-groups.io-blue)](https://groups.io/g/CycloneDX)\n[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Follow)](https://twitter.com/CycloneDX_Spec)\n\n----\n\nThis project provides a runnable Python-based application for generating CycloneDX bill-of-material documents from either:\n1. Your current Python Environment\n2. Your project's manifest (e.g. `requirements.txt`)\n\nThe BOM will contain an aggregate of all your current project's dependencies, or those defined by the manifest you supply.\n\nCycloneDX is a lightweight BOM specification that is easily created, human-readable, and simple to parse.\n\n## Installation\n\nInstall this from [PyPi.org](https://pypi.org/project/cyclonedx-bom/) using your preferred Python package manager.\n\nExample using `pip`:\n```\npip install cyclonedx-bom\n```\n\nExample using `poetry`:\n```\npoetry add cyclonedx-bom\n```\n\n## Usage\n\nOnce installed, you can access the full documentation by running `--help`:\n\n```\n$ cyclonedx-py --help\nusage: cyclonedx-py [-h] (-e | -r) [-rf FILE_PATH] [--format {json,xml}] [--schema-version {1.3,1.2,1.1,1.0}] \n[-o FILE_PATH] [-F] [-X]\n\nCycloneDX SBOM Generator\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -e, --e, --environment\n                        Build a SBOM based on the packages installed in your current Python environment (default)\n  -r, --r, --requirements\n                        Build a SBOM based on a requirements.txt's contents\n  -X                    Enable debug output\n\nRequirements:\n  Additional optional arguments if you are setting the input type to `requirements`.\n\n  -rf FILE_PATH, --rf FILE_PATH, --requirements-file FILE_PATH\n                        Path to a the requirements.txt file you wish to parse\n\nSBOM Output Configuration:\n  Choose the output format and schema version\n\n  --format {json,xml}   The output format for your SBOM (default: xml)\n  --schema-version {1.3,1.2,1.1,1.0}\n                        The CycloneDX schema version for your SBOM (default: 1.3)\n  -o FILE_PATH, --o FILE_PATH, --output FILE_PATH\n                        Output file path for your SBOM (set to '-' to output to STDOUT)\n  -F, --force           If outputting to a file and the stated file already exists, it will be overwritten.\n```\n\n### Building CycloneDX for your current Python environment\n\nThis will produce the most accurate and complete CycloneDX BOM as it will include all transitive dependencies required\nby the packages defined in your project's manifest (think `requriements.txt`).\n\nSimply run:\n\n```\ncyclonedx-py -e -o -\n```\n\nThis will generate a CycloneDX including all packages installed in your current Python environment and output to STDOUT\nin XML using the latest schema version `1.3` by default.\n\n\n### Building CycloneDX from your Manifest\n\nWe currently support `requirements.txt` manifest files. Note that a BOM such as CycloneDX expects exact version numbers, \ntherefore if you wish to generate a BOM from a `requirements.txt`, these must be frozen. This can be accomplished via:\n\n```\npip freeze > requirements.txt\n```\n\nYou can then run `cyclonedx-py` as follows:\n```\ncyclonedx-py -r -rf PATH/TO/requirements.txt -o -\n```\n\nThis will generate a CycloneDX and output to STDOUT in XML using the latest schema version `1.3` by default.\n\n## Python Support\n\nWe endeavour to support all functionality for all [current actively supported Python versions](https://www.python.org/downloads/).\nHowever, some features may not be possible/present in older Python versions due to their lack of support.\n\n## Copyright & License\n\nCycloneDX BOM is Copyright (c) OWASP Foundation. All Rights Reserved.\n\nPermission to modify and redistribute is granted under the terms of the Apache 2.0 license.",
    'author': 'Steven Springett',
    'author_email': 'steve.springett@owasp.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CycloneDX/cyclonedx-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
