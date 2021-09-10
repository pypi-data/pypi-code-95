# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_hypermodel']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.65.2', 'pydantic>=1.8.0,<2.0.0']

setup_kwargs = {
    'name': 'fastapi-hypermodel',
    'version': '0.2.8',
    'description': 'A FastAPI + Pydantic extension for simplifying hypermedia-driven API development.',
    'long_description': '# FastAPI-HyperModel\n\nFastAPI-HyperModel is a FastAPI + Pydantic extension for simplifying hypermedia-driven API development. This module adds a new Pydantic model base-class, supporting dynamic `href` generation based on object data.\n\n## Installation\n\n`pip install fastapi-hypermodel`\n\n## Basic Usage\n\n### Import `HyperModel` and optionally `HyperRef`\n\n```python\nfrom fastapi import FastAPI\n\nfrom fastapi_hypermodel import HyperModel, UrlFor, LinkSet\n```\n\n`HyperModel` will be your model base-class.\n\n### Create your basic models\n\nWe\'ll create two models, a brief item summary including ID, name, and a link, and a full model containing additional information. We\'ll use `ItemSummary` in our item list, and `ItemDetail` for full item information.\n\n```python\nclass ItemSummary(HyperModel):\n    id: str\n    name: str\n\nclass ItemDetail(ItemSummary):\n    description: Optional[str] = None\n    price: float\n\nclass Person(HyperModel):\n    name: str\n    id: str\n    items: List[ItemSummary]\n```\n\n### Create and attach your app\n\nWe\'ll now create our FastAPI app, and bind it to our `HyperModel` base class.\n\n```python\nfrom fastapi import FastAPI\n\napp = FastAPI()\nHyperModel.init_app(app)\n```\n\n### Add some API views\n\nWe\'ll create an API view for a list of items, as well as details about an individual item. Note that we pass the item ID with our `{item_id}` URL variable.\n\n```python\n@app.get("/items", response_model=List[ItemSummary])\ndef read_items():\n    return list(items.values())\n\n@app.get("/items/{item_id}", response_model=ItemDetail)\ndef read_item(item_id: str):\n    return items[item_id]\n\n@app.get("/people/{person_id}", response_model=Person)\ndef read_person(person_id: str):\n    return people[person_id]\n\n@app.get("/people/{person_id}/items", response_model=List[ItemDetail])\ndef read_person_items(person_id: str):\n    return people[person_id]["items"]\n```\n\n### Create a model `href`\n\nWe\'ll now go back and add an `href` field with a special `UrlFor` value. This `UrlFor` class defines how our href elements will be generated. We\'ll change our `ItemSummary` class to:\n\n```python\nclass ItemSummary(HyperModel):\n    name: str\n    id: str\n    href = UrlFor("read_item", {"item_id": "<id>"})\n```\n\nThe `UrlFor` class takes two arguments:\n\n#### `endpoint`\n\nName of your FastAPI endpoint function you want to link to. In our example, we want our item summary to link to the corresponding item detail page, which maps to our `read_item` function.\n\n#### `values` (optional depending on endpoint)\n\nSame keyword arguments as FastAPI\'s url_path_for, except string arguments enclosed in < > will be interpreted as attributes to pull from the object. For example, here we need to pass an `item_id` argument as required by our endpoint function, and we want to populate that with our item object\'s `id` attribute.\n\n### Create a link set\n\nIn some cases we want to create a map of relational links. In these cases we can create a `LinkSet` field describing each link and it\'s relationship to the object.\n\n```python\nclass Person(HyperModel):\n    id: str\n    name: str\n    items: List[ItemSummary]\n\n    href = UrlFor("read_person", {"person_id": "<id>"})\n    links = LinkSet(\n        {\n            "self": UrlFor("read_person", {"person_id": "<id>"}),\n            "items": UrlFor("read_person_items", {"person_id": "<id>"}),\n        }\n    )\n```\n\n### Putting it all together\n\nFor this example, we can make a dictionary containing some fake data, and add extra models, even nesting models if we want. A complete example based on this documentation can be found [here](examples/simple_app.py).\n\nIf we run the example application and go to our `/items` URL, we should get a response like:\n\n```json\n[\n  {\n    "name": "Foo",\n    "id": "item01",\n    "href": "/items/item01"\n  },\n  {\n    "name": "Bar",\n    "id": "item02",\n    "href": "/items/item02"\n  },\n  {\n    "name": "Baz",\n    "id": "item03",\n    "href": "/items/item03"\n  }\n]\n```\n\n## Limitations\n\nCurrently, query parameters will not resolve correctly. When generating a resource URL, ensure all parameters passed are path parameters, not query parameters.\n\nThis is an upstream issue, being tracked [here](https://github.com/encode/starlette/issues/560).\n\n## Attributions\n\nSome functionality is based on [Flask-Marshmallow](https://github.com/marshmallow-code/flask-marshmallow/blob/dev/src/flask_marshmallow/fields.py) `URLFor` class.\n',
    'author': 'Joel Collins',
    'author_email': 'joel.collins@renalregistry.nhs.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jtc42/fastapi-hypermodel',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
