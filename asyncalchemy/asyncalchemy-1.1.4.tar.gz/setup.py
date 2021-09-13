# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asyncalchemy']

package_data = \
{'': ['*']}

install_requires = \
['sqlalchemy>=1.2.0,<1.4.0']

setup_kwargs = {
    'name': 'asyncalchemy',
    'version': '1.1.4',
    'description': 'A thin async wrapper for SQLAlchemy sessions.',
    'long_description': '# AsyncAlchemy\nA thin async wrapper for [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) sessions.\n\nBesides being async, the wrapper manages the context of the session for the execution block.Commits incoming changes if successfull or rolls back changes if an exceptions occurs.\\\n*Note*: The upcoming SQLAlchemy 1.4 version will include built-in async functionality, it\'s recommended to upgrade to it once it\'s [released](https://github.com/sqlalchemy/sqlalchemy/releases).\n\n\n## Install\n### Pip\n```bash\npip install asyncalchemy\n```\n\n### From Source\nThe project uses [poetry](https://github.com/python-poetry/poetry) for dependency management and packaging.\\\nTo run from source clone project and:\n```bash\npip install poetry\npoetry install\n```\n\n\n## Usage\n### Basic Example\n```python\nfrom asyncalchemy import create_session_factory\n\n# Create AsyncAlchemy session factory\nsession_factory = create_session_factory(db_uri, Base)\n\n# Create session\nasync with session_factory() as session:\n    await session.query(Something).filter_by(something="else")\n```\n\n### Example With Extra Params\n```python\nfrom sqlalchemy.pool import NullPool\n\nfrom asyncalchemy import create_session_factory\n\n# Create session factory with additional SQLAlchemy params\nsession_factory = create_session_factory(db_uri, Base, poolclass=NullPool)\n\n# Create session\nasync with session_factory() as session:\n    await second_session.add(Something)\n    await second_session.flush()\n\n    # Reuse session\n    async with session_factory(reuse_session=session) as second_session:\n        await session.delete(Something)\n```\n',
    'author': 'Claroty Open Source',
    'author_email': 'opensource@claroty.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/claroty/AsyncAlchemy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
