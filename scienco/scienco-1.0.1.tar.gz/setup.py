# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scienco', 'scienco.indexes', 'scienco.metrics']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'scienco',
    'version': '1.0.1',
    'description': 'Calculate the readability of text using one of a variety of computed indexes',
    'long_description': 'Scienco\n=======\n[![pipeline status][pipeline]][homepage]\n[![coverage report][coverage]][homepage]\n[![latest version][version]][pypi]\n[![python requires][pyversions]][pypi]\n\nCalculate the readability of text using one of a variety of computed indexes including:\n\n- Flesch-Kincaid score\n- Automated readability index\n- Coleman-Liau index\n\nRequirements\n------------\nPython 3.8+\n\nInstallation\n------------\n```\n$ pip install scienco\n```\n\nUsage\n-----\n```python\n>>> import scienco\n>>> metrics = scienco.compute_metrics("Lorem ipsum dolor sit amet ...")\n>>> metrics\nMetrics(sentences=32, words=250, letters=1329, syllables=489, is_russian=False)\n>>> indexes = scienco.compute_indexes(sentences=32, words=250, letters=1329, syllables=489, is_russian=False)\n>>> indexes\nIndexes(flesch_reading_ease_score=33.43, automated_readability_index=7.51, coleman_liau_index=11.67)\n```\n\nDistribution\n------------\nThis project is licensed under the terms of the [MIT License](LICENSE).\n\nLinks\n-----\n- Documentation: <https://amalchuk.gitlab.io/scienco>\n- Code: <https://gitlab.com/amalchuk/scienco>\n- GitHub mirror: <https://github.com/amalchuk/scienco>\n\n[homepage]: <https://gitlab.com/amalchuk/scienco>\n[pypi]: <https://pypi.org/project/scienco>\n[pipeline]: <https://gitlab.com/amalchuk/scienco/badges/master/pipeline.svg?style=flat-square>\n[coverage]: <https://gitlab.com/amalchuk/scienco/badges/master/coverage.svg?style=flat-square>\n[version]: <https://img.shields.io/pypi/v/scienco?color=blue&style=flat-square>\n[pyversions]: <https://img.shields.io/pypi/pyversions/scienco?color=blue&style=flat-square>\n',
    'author': 'Andrew Malchuk',
    'author_email': 'andrew.malchuk@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/amalchuk/scienco',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
