# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bareasgi_graphql_next',
 'bareasgi_graphql_next.graphene',
 'bareasgi_graphql_next.graphql']

package_data = \
{'': ['*']}

install_requires = \
['bareASGI>=3,<4', 'graphql-core>=3.1,<4.0']

extras_require = \
{'graphene': ['graphene>=3.0b7,<4.0']}

setup_kwargs = {
    'name': 'bareasgi-graphql-next',
    'version': '4.1.0',
    'description': 'GraphQL support for the bareASGI framework',
    'long_description': "# bareASGI-graphql-next\n\nGraphql support for [bareASGI](http://github.com/rob-blackbourn/bareASGI) (read the [documentation](https://rob-blackbourn.github.io/bareASGI-graphql-next/))\n\nThe controller provides a GraphQL GET and POST route, a WebSocket subscription server, and a Graphiql view.\n\n## Installation\n\nInstall from the pie shop.\n\n```bash\npip install bareasgi-graphql-next\n```\n\nIf you wish to install with the grapheme option:\n\n```bash\npip install 'bareasgi-graphql-next[graphene]'\n```\n\n## Usage\n\nYou can register the graphql controller with the `add_graphql_next` function.\n\n```python\nfrom bareasgi import Application\nfrom bareasgi_graphql_next import add_graphql_next\nimport graphql\n\n# Get the schema ...\nschema = graphql.GraphQLSchema( ... )\n\nimport uvicorn\n\napp = Application()\nadd_graphql_next(app, schema)\n\nuvicorn.run(app, port=9009)\n\n```\n\n## Development\n\nTo develop with the graphene optional package:\n\n```bash\npoetry install --extras graphene\n```\n",
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rob-blackbourn/bareasgi-graphql-next',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
