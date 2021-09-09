# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sqlalchemy_ibmi']

package_data = \
{'': ['*']}

install_requires = \
['pyodbc>=4.0', 'sqlalchemy>=1.3']

entry_points = \
{'sqlalchemy.dialects': ['ibmi = sqlalchemy_ibmi.base:IBMiDb2Dialect']}

setup_kwargs = {
    'name': 'sqlalchemy-ibmi',
    'version': '0.9.1',
    'description': 'SQLAlchemy support for Db2 on IBM i',
    'long_description': '[![Latest version released on PyPi](https://img.shields.io/pypi/v/sqlalchemy-ibmi.svg)](https://pypi.org/project/sqlalchemy-ibmi)\n![Supported Python Version Badge](https://img.shields.io/pypi/pyversions/sqlalchemy-ibmi.svg)\n[![GitHub Actions status | sdras/awesome-actions](https://github.com/IBM/sqlalchemy-ibmi/workflows/Build%20PR/badge.svg)](https://github.com/IBM/sqlalchemy-ibmi/actions?workflow=Build+PR)\n[![Documentation Status](https://readthedocs.org/projects/sqlalchemy-ibmi/badge/?version=latest)](https://sqlalchemy-ibmi.readthedocs.io/en/latest/?badge=latest)\n\n\nSQLAlchemy adapter for IBM i\n=========\n\nThe IBM i SQLAlchemy adapter provides a [SQLAlchemy](https://www.sqlalchemy.org/) interface to Db2 for [IBM i](https://en.wikipedia.org/wiki/IBM_i).\n\n**Please note that this project is still under active development. Please\n report any bugs in the issue tracker** :rotating_light: \n\n```python\nimport sqlalchemy as sa\n\n# see documentation for available connection options\n# pass connection options in url query string, eg.\n# engine = sa.create_engine("ibmi://user:pass@host?autocommit=true&timeout=10"\n# find usage of create_engine database urls here\n# https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls\n# this is the base connection which connects to *LOCAL on the host\n\nengine = sa.create_engine("ibmi://user:pass@host")\n\ncnxn = engine.connect()\nmetadata = sa.MetaData()\ntable = sa.Table(\'table_name\', metadata, autoload=True, autoload_with=engine)\n\nquery = sa.select([table])\n\nresult = cnxn.execute(query)\nresult = result.fetchall()\n\n# print first entry\nprint(result[0])\n\n```\n\nInstallation\n-------------\n```sh\npip install sqlalchemy-ibmi\n```\n \nFeature Support\n----------------\n- SQLAlchemy ORM  - Python object based automatically constructed SQL\n- SQLAlchemy Core - schema-centric SQL Expression Language\n\nDocumentation\n-------------\n\nThe documentation for the SQLAlchemy adapter for IBM i can be found at:\nhttps://sqlalchemy-ibmi.readthedocs.io/en/latest/\n\n\nKnown Limitations \n-------------------------------------------------------------\n1) Non-standard SQL queries are not supported. e.g. "SELECT ? FROM TAB1"\n2) For updations involving primary/foreign key references, the entries should be made in correct order. Integrity check is always on and thus the primary keys referenced by the foreign keys in the referencing tables should always exist in the parent table.\n3) Unique key which contains nullable column not supported\n4) UPDATE CASCADE for foreign keys not supported\n5) DEFERRABLE INITIALLY deferred not supported\n6) Subquery in ON clause of LEFT OUTER JOIN not supported\n\nContributing to the IBM i SQLAlchemy adapter\n----------------------------------------\nPlease read the [contribution guidelines](contributing/CONTRIBUTING.md).\n\n```\nThe developer sign-off should include the reference to the DCO in remarks(example below):\nDCO 1.1 Signed-off-by: Random J Developer <random@developer.org>\n```\n\nLicense\n-------\n\n[Apache 2.0](LICENSE)\n\nCredits\n-------\n- ibm_db_sa for SQLAlchemy was first produced by IBM Inc., targeting version 0.4.\n- The library was ported for version 0.6 and 0.7 by Jaimy Azle.\n- Port for version 0.8 and modernization of test suite by Mike Bayer.\n- Port for sqlalchemy-ibmi by Naveen Ram/Kevin Adler.\n',
    'author': 'Naveen Ram',
    'author_email': 'naveen.ram@ibm.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
