# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydbrepo',
 'pydbrepo.decorators',
 'pydbrepo.descriptors',
 'pydbrepo.drivers',
 'pydbrepo.entity',
 'pydbrepo.errors',
 'pydbrepo.helpers',
 'pydbrepo.helpers.common',
 'pydbrepo.helpers.mongo',
 'pydbrepo.helpers.mysql',
 'pydbrepo.helpers.sql',
 'pydbrepo.helpers.sqlite',
 'pydbrepo.repository']

package_data = \
{'': ['*']}

install_requires = \
['PyPika>=0.48.7,<0.49.0', 'python-dateutil>=2.8.2,<3.0.0']

setup_kwargs = {
    'name': 'pydbrepo',
    'version': '0.6.1',
    'description': 'Simple implementation of repository pattern for database connections.',
    'long_description': '# PyDBRepo\n\nIs a simple implementation of the Repository pattern to access data in python, providing extensibility flexibility\nand builtin tools to manage databases with this pattern.\n\n## Supported databases\n\n- SQLite\n- MySQL\n- PostgreSQL\n- MongoDB\n\n## Requirements\n\n- Python >= 3.7\n\n### Postgres\n\n- psychopg2-binary\n\n### Mysql\n\n- mysql-connector-python\n\n### MongoDB\n\n- pymongo\n- dnspython\n\n\n## Examples\n\n### Entity usage\n\n#### Entity model\n\nThis class brings the build it in methods: \n\n- `to_dict`: Will take all properties of the created class and will convert it into a dict instance.\n- `from_dict`: This will take a dict instance and will set the values of every key into a model property with\n  the same name.\n- `from_record`: It takes an ordered Iterable object with the name of the fields that will be loaded into the model,\n  and a tuple with the corresponding values\n\nEntity models will be used with simple class properties or can be used with the `Field` descriptor of the package\n\n##### Example with simple properties\n\n```python\nfrom pydbrepo import Entity\n\nclass Model(Entity):\n    id = None\n    name = None\n\nmodel = Model.from_dict({"id": 1, "name": "some"})\n# Model({"id": 1, "name": "some"})\n\nprint(model.id) # => 1\nprint(model.name) # => some\n```\n\n##### Example with property decorators\n\n```python\nfrom pydbrepo import Entity\n\nclass Model(Entity):\n    def __init__(self):\n        super().__init__()\n        \n        self.id = None\n        self.name = None\n        \n    @property\n    def id(self):\n        return self._id\n    \n    @id.setter\n    def id(self, value):\n        self._id = value\n        \n    @property\n    def name(self):\n        return self._name\n    \n    @name.setter\n    def name(self, value):\n        self._name = value\n\nmodel = Model.from_dict({"id": 1, "name": "some"})\n# Model({"id": 1, "name": "some"})\n\nprint(model.id) # => 1\nprint(model.name) # => some\n```\n\n##### Example with Field descriptor\n\n```python\nfrom pydbrepo import Entity, Field, named_fields\n\n@named_fields\nclass Model(Entity):\n    id = Field(type_=int)\n    name = Field(type_=str)\n\nmodel = Model.from_dict({"id": 1, "name": "some"})\n# Model({"id": 1, "name": "some"})\n\nprint(model.id) # => 1\nprint(model.name) # => some\n```\n\n##### Example of casting values with Field descriptor\n\n```python\nfrom uuid import UUID\nfrom pydbrepo import Entity, Field, named_fields\n\n@named_fields\nclass Model(Entity):\n    id = Field(type_=(UUID, str), cast_to=UUID, cast_if=str)\n    name = Field(type_=str)\n\nmodel = Model.from_dict({"id": \'10620c02-d80e-4950-b0a2-34a5f2d34ae5\', "name": "some"})\n# Model({"id": UUID(\'10620c02-d80e-4950-b0a2-34a5f2d34ae5\'), "name": "some"})\n\nprint(model.id) # => 10620c02-d80e-4950-b0a2-34a5f2d34ae5\nprint(model.name) # => some\n```\n\n##### Example of iterable fields and casting with Field descriptor\n\n```python\nfrom pydbrepo import Entity, Field, named_fields\n\n@named_fields\nclass Item(Entity):\n    name = Field(type_=str)\n    price = Field(type_=float)\n\n@named_fields\nclass Model(Entity):\n    id = Field(type_=int)\n    name = Field(type_=str)\n    items = Field(type_=list, cast_items_to=Item)\n\nmodel = Model.from_dict({\n    "id": 1, \n    "name": "some", \n    "items": [\n        {"name": "some", "price": 5.99},\n        {"name": "nothing", "price": 6.99},\n    ]\n})\n# Model({"id": 1, "name": "some", "items": [Item({"name": "some", "price": 5.99}), Item({"name": "nothing", "price": 6.99})]})\n\nprint(model.id) # => 1\nprint(model.name) # => some\nprint(model.items) # => [Item({"name": "some", "price": 5.99}), Item({"name": "nothing", "price": 6.99})]\nprint(model.items[0].price) # => 5.99\n```\n',
    'author': 'Eduardo Aguilar',
    'author_email': 'dante.aguilar41@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/danteay/pydbrepo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
