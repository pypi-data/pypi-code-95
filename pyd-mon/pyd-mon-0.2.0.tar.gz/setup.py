# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyd_mon']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0', 'pymongo>=3.12.0,<4.0.0']

setup_kwargs = {
    'name': 'pyd-mon',
    'version': '0.2.0',
    'description': "A super small package for validating and converting MongoDB ObjectId's to Pydantic models.",
    'long_description': "# Pyd_Mon\n\nAn easy way to convert and validate Pymongo ObjectId's with Pydantic model fields.\n\n# Usage\n\n## Creating a MongoModel\n\nCreating Pydantic models with a mapping id is as easy as inheriting from MongoModel and creating an `id` field with type of `MongoId`. All of your other fields can be created as normal pydantic fields.\n\n```python\nfrom pyd_mon import MongoModel, MongoId\n\nclass Item(MongoModel):\n    id: MongoId # Will map to '_id'\n    name: str # The rest of the fields are standard Pydantic fields\n```\n\n## Create Pydantic instance from Pymongo dict (`_id` -> `id`)\n\nTo map from a Pymongo dict you can use the `from_mongo` class method on your model.\n\n```python\nresult = collection.find_one() # Get item from Pymongo\nitem = Item.from_mongo(result) # Create a Pydantic instance from the Pymongo dict.\n```\n\n## Create Pymongo dict from Pydantic instance (`id` -> `_id`)\n\nTo map back from a pydantic instance to a Pymongo dict call the `mongo` method on your model instance.\n\n```python\nitem = Item(id=MongoId(), name='Example')\ncollection.insert_one(item.mongo())\n```\n",
    'author': 'Trevor Hodsdon',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MrTj458/pyd-mon',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
