# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ra_flatfile_importer']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'ra-utils>=0.4.0,<0.5.0',
 'raclients>=0.4.3,<0.5.0',
 'ramodels>=2.1.1,<3.0.0',
 'tqdm>=4.60.0,<5.0.0']

setup_kwargs = {
    'name': 'ra-flatfile-importer',
    'version': '0.1.2',
    'description': 'Flatfile importer for OS2mo/LoRa',
    'long_description': '<!--\nSPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>\nSPDX-License-Identifier: MPL-2.0\n-->\n\n\n# RA Flatfile importer\n\nOS2mo/LoRa flatfile importer.\n\n## Build\n```\ndocker build . -t ra-flatfile-importer\n```\nWhich yields:\n```\n...\nSuccessfully built ...\nSuccessfully tagged ra-flatfile-importer:latest\n```\nAfter which you can run:\n```\ndocker run --rm ra-flatfile-importer\n```\nWhich yields:\n```\nUsage: flatfile_importer.py [OPTIONS] COMMAND [ARGS]...\n\n  Flatfile importer.\n\n    Used to validate and load flatfile data (JSON) into OS2mo/LoRa.\n\n  Options:\n    --help  Show this message and exit.\n\n  Commands:\n    lora  Lora Flatfile importer.\n    mo    OS2mo Flatfile importer.\n```\n\n## Usage\nThe primary usage of the tool is to upload flat-files to LoRa / OS2mo.\n```\ndocker run --rm ra-flatfile-importer lora upload < lora.json\ndocker run --rm ra-flatfile-importer mo upload < mo.json\n```\n\nThe tool can generate dummy files to test out this functionality:\n```\ndocker run --rm ra-flatfile-importer lora generate --name "Aarhus Kommune" > lora.json\ndocker run --rm ra-flatfile-importer mo generate --name "Aarhus Kommune" > mo.json\n```\nThese test files should be uploadable to Lora/MO and produce a valid MO instance.\n\n\nThe tool has various other commands too, such as producing the validation schema for the flat file format:\n```\ndocker run --rm ra-flatfile-importer lora schema --indent 4\n```\nWhich yields:\n```\n{\n    "title": "LoraFlatFileFormatModel",\n    "description": "Flatfile format for LoRa.\\n\\nMinimal valid example is {}.",\n    "type": "object",\n    "properties": {\n        "facetter": {\n           ...\n        },\n        ...\n    }\n}\n```\nOr for validating whether a file is invalid:\n```\ndocker run --rm ra-flatfile-importer lora validate < lora.json\n```\n\n## Versioning\nThis project uses [Semantic Versioning](https://semver.org/) with the following strategy:\n- MAJOR: Incompatible changes to existing commandline interface\n- MINOR: Backwards compatible updates to commandline interface\n- PATCH: Backwards compatible bug fixes\n\nThe fileformat is versioned directly, and the version is exported in the file itself.\n\n<!--\n## Getting Started\n\nTODO: README section missing!\n\n### Prerequisites\n\n\nTODO: README section missing!\n\n### Installing\n\nTODO: README section missing!\n\n## Running the tests\n\nTODO: README section missing!\n\n## Deployment\n\nTODO: README section missing!\n\n## Built With\n\nTODO: README section missing!\n\n## Authors\n\nMagenta ApS <https://magenta.dk>\n\nTODO: README section missing!\n-->\n## License\n- This project: [MPL-2.0](MPL-2.0.txt)\n- Dependencies:\n  - pydantic: [MIT](MIT.txt)\n\nThis project uses [REUSE](https://reuse.software) for licensing. All licenses can be found in the [LICENSES folder](LICENSES/) of the project.\n',
    'author': 'Magenta',
    'author_email': 'info@magenta.dk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://magenta.dk/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
