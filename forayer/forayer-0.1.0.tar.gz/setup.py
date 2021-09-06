# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['forayer',
 'forayer.datasets',
 'forayer.exploration',
 'forayer.input_output',
 'forayer.knowledge_graph',
 'forayer.transformation',
 'forayer.utils']

package_data = \
{'': ['*']}

install_requires = \
['gensim>=4.0.1,<5.0.0',
 'importlib-metadata',
 'ipykernel>=6.2.0,<7.0.0',
 'joblib>=1.0.1,<2.0.0',
 'nbformat>=5.1.3,<6.0.0',
 'numpydoc>=1.1.0,<2.0.0',
 'pandas>=1.3.2,<2.0.0',
 'plotly>=5.2.1,<6.0.0',
 'rdflib>=6.0.0,<7.0.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'tqdm>=4.56.0,<5.0.0',
 'wget>=3.2,<4.0']

extras_require = \
{'docs': ['sphinx>=4.0.2,<5.0.0', 'insegel>=1.1.0,<2.0.0']}

setup_kwargs = {
    'name': 'forayer',
    'version': '0.1.0',
    'description': 'First aid utilies for knowledge graph exploration with an entity centric approach',
    'long_description': '<p align="center">\n<img src="https://github.com/dobraczka/forayer/raw/main/docs/forayerlogo.png" alt="forayer logo", width=200/>\n</p>\n\n<h2 align="center"> forayer</h2>\n\n<p align="center">\n<a href="https://github.com/dobraczka/forayer/actions/workflows/main.yml"><img alt="Tests" src="https://github.com/dobraczka/forayer/actions/workflows/tests.yml/badge.svg?branch=main"></a>\n<a href="https://github.com/dobraczka/forayer/actions/workflows/quality.yml"><img alt="Linting" src="https://github.com/dobraczka/forayer/actions/workflows/quality.yml/badge.svg?branch=main"></a>\n<a><img alt="Test coverage" src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/dobraczka/6d07d95e43929bcbf9d031c2c8f2015f/raw/forayer_test_gist.json"></a>\n<a href="https://pypi.org/project/forayer"/><img alt="Stable python versions" src="https://img.shields.io/pypi/pyversions/forayer"></a>\n<a href="https://github.com/dobraczka/forayer/blob/main/LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue"></a>\n<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n</p>\n\nAbout\n=====\nForayer is a library of **f**irst aid utilities for kn**o**wledge g**r**aph explor**a**tion with an entit**y** c**e**ntric app**r**oach.\nIt is intended to make data integration of knowledge graphs easier. With entities as first class citizens forayer is a toolset to aid in knowledge graph exploration for data integration and specifically entity resolution.\n\nYou can easily load pre-existing entity resolution tasks:\n\n```python\n  >>> from forayer.datasets import OpenEADataset\n  >>> ds = OpenEADataset(ds_pair="D_W",size="15K",version=1)\n  >>> ds.er_task\n  ERTask({DBpedia: (# entities: 15000, # entities_with_rel: 15000, # rel: 13359,\n  # entities_with_attributes: 13782, # attributes: 13782, # attr_values: 24995),\n  Wikidata: (# entities: 15000, # entities_with_rel: 15000, # rel: 13554,\n  # entities_with_attributes: 14376, # attributes: 14376, # attr_values: 114107)},\n  ClusterHelper(# elements:30000, # clusters:15000))\n```\n\nThis entity resolution task holds 2 knowledge graphs and a cluster of known matches. You can search in knowledge graphs:\n\n```python\n  >>> ds.er_task["DBpedia"].search("Dorothea")\n  KG(entities={\'http://dbpedia.org/resource/E801200\': \n  {\'http://dbpedia.org/ontology/activeYearsStartYear\': \'"1948"^^<http://www.w3.org/2001/XMLSchema#gYear>\',\n  \'http://dbpedia.org/ontology/activeYearsEndYear\': \'"2008"^^<http://www.w3.org/2001/XMLSchema#gYear>\',\n  \'http://dbpedia.org/ontology/birthName\': \'Dorothea Carothers Allen\',\n  \'http://dbpedia.org/ontology/alias\': \'Allen, Dorothea Carothers\',\n  \'http://dbpedia.org/ontology/birthYear\': \'"1923"^^<http://www.w3.org/2001/XMLSchema#gYear>\',\n  \'http://purl.org/dc/elements/1.1/description\': \'Film editor\',\n  \'http://dbpedia.org/ontology/birthDate\': \'"1923-12-03"^^<http://www.w3.org/2001/XMLSchema#date>\',\n  \'http://dbpedia.org/ontology/deathDate\': \'"2010-04-17"^^<http://www.w3.org/2001/XMLSchema#date>\', \n  \'http://dbpedia.org/ontology/deathYear\': \'"2010"^^<http://www.w3.org/2001/XMLSchema#gYear>\'}}, rel={}, name=DBpedia)\n```\n\nDecide to work with a smaller snippet of the resolution task:\n\n```python\n  >>> ert_sample = ds.er_task.sample(100)\n  >>> ert_sample\n  ERTask({DBpedia: (# entities: 100, # entities_with_rel: 6, # rel: 4,\n  # entities_with_attributes: 99, # attributes: 99, # attr_values: 274),\n  Wikidata: (# entities: 100, # entities_with_rel: 4, # rel: 4,\n  # entities_with_attributes: 100, # attributes: 100, # attr_values: 797)},\n  ClusterHelper(# elements:200, # clusters:100))\n```\n\nAnd much more can be found in the [user guide](https://forayer.readthedocs.io/en/latest/source/user_guide.html).\n\nInstallation\n============\n\nYou can install forayer via pip:\n\n```bash\n  pip install forayer\n```\n',
    'author': 'Daniel Obraczka',
    'author_email': 'obraczka@informatik.uni-leipzig.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dobraczka/forayer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
