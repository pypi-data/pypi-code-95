# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flashgeotext']

package_data = \
{'': ['*'], 'flashgeotext': ['resources/*']}

install_requires = \
['flashtext>=2.7,<3.0', 'loguru>=0.5.3,<0.6.0', 'pydantic>=1.8,<2.0']

setup_kwargs = {
    'name': 'flashgeotext',
    'version': '0.4.0',
    'description': 'Extract and count countries and cities (+their synonyms) from text',
    'long_description': '<p align="center">\n<a href="https://github.com/iwpnd/flashgeotext/actions" target="_blank">\n    <img src="https://github.com/iwpnd/flashgeotext/workflows/build/badge.svg?branch=master" alt="Build Status">\n</a>\n<a href="https://codecov.io/gh/iwpnd/flashgeotext" target="_blank">\n    <img src="https://codecov.io/gh/iwpnd/flashgeotext/branch/master/graph/badge.svg" alt="Coverage">\n</a>\n</p>\n\n---\n\n# flashgeotext :zap::earth_africa:\n\nExtract and count countries and cities (+their synonyms) from text, like [GeoText](https://github.com/elyase/geotext) on steroids using [FlashText](https://github.com/vi3k6i5/flashtext/), a Aho-Corasick implementation. Flashgeotext is a fast, batteries-included (and BYOD) and native python library that extracts one or more sets of given city and country names (+ synonyms) from an input text.\n\n**documentation**: [https://flashgeotext.iwpnd.pw/](https://flashgeotext.iwpnd.pw/)  \n**introductory blogpost**: [https://iwpnd.pw/articles/2020-02/flashgeotext-library](https://iwpnd.pw/articles/2020-02/flashgeotext-library)\n\n## Usage\n\n```python\nfrom flashgeotext.geotext import GeoText\n\ngeotext = GeoText()\n\ninput_text = \'\'\'Shanghai. The Chinese Ministry of Finance in Shanghai said that China plans\n                to cut tariffs on $75 billion worth of goods that the country\n                imports from the US. Washington welcomes the decision.\'\'\'\n\ngeotext.extract(input_text=input_text)\n>> {\n    \'cities\': {\n        \'Shanghai\': {\n            \'count\': 2,\n            \'span_info\': [(0, 8), (45, 53)],\n            \'found_as\': [\'Shanghai\', \'Shanghai\'],\n            },\n        \'Washington, D.C.\': {\n            \'count\': 1,\n            \'span_info\': [(175, 185)],\n            \'found_as\': [\'Washington\'],\n            }\n        },\n    \'countries\': {\n        \'China\': {\n            \'count\': 1,\n            \'span_info\': [(64, 69)],\n            \'found_as\': [\'China\'],\n            },\n        \'United States\': {\n            \'count\': 1,\n            \'span_info\': [(171, 173)],\n            \'found_as\': [\'US\'],\n            }\n        }\n    }\n```\n\n## Getting Started\n\nThese instructions will get you a copy of the project up and running on your local machine for development and testing purposes.\n\n### Installing\n\npip:\n\n```bash\npip install flashgeotext\n```\n\nconda:\n\n```bash\nconda install flashgeotext\n```\n\nfor development:\n\n```bash\ngit clone https://github.com/iwpnd/flashgeotext.git\ncd flashgeotext/\npoetry install\n```\n\n### Running the tests\n\n```bash\npoetry run pytest . -v\n```\n\n## Authors\n\n- **Benjamin Ramser** - _Initial work_ - [iwpnd](https://github.com/iwpnd)\n\nSee also the list of [contributors](https://github.com/iwpnd/flashgeotext/contributors) who participated in this project.\n\n## License\n\nThis project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details\n\nDemo Data cities from [http://www.geonames.org](http://www.geonames.org) licensed under the Creative Commons Attribution 3.0 License.\n\n## Acknowledgments\n\n- Hat tip to [@vi3k6i5](https://github.com/vi3k6i5) for his [paper](https://arxiv.org/abs/1711.00046) and implementation\n',
    'author': 'Benjamin Ramser',
    'author_email': 'ahoi@iwpnd.pw',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://flashgeotext.iwpnd.pw',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
