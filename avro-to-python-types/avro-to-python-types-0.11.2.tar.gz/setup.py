# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['avro_to_python_types']

package_data = \
{'': ['*']}

install_requires = \
['fastavro>=1.4.4,<2.0.0']

entry_points = \
{'console_scripts': ['sync-example = examples:generate_types_from_schemas']}

setup_kwargs = {
    'name': 'avro-to-python-types',
    'version': '0.11.2',
    'description': 'A library for converting avro schemas to python types.',
    'long_description': '# avro-to-python-types\n\nA library for converting avro schemas to python types.\n\nCurrently, it supports converting `record`s to `TypedDict`. If you would like to see more features added, please open up an issue.\n\n## Why would I want this?\n\nThis library is targeted to people writing code generation for python apps that are using [avro](https://avro.apache.org/docs/current/spec.html).\n\n## Usage\n\nThis library does [one thing](https://en.wikipedia.org/wiki/Unix_philosophy#Do_One_Thing_and_Do_It_Well), it converts Avro schemas to python types.\n\nTo get up and running quickly, you can use this to simply load schemas and print out the python\ncode that is generated.\n\n```python\nimport glob\nfrom avro_to_python_types import typed_dict_from_schema_file\n\nschema_files = glob.glob("schemas/*.avsc")\n\nfor schema_file in schema_files:\n    types = typed_dict_from_schema_file(schema_file)\n    print(types) \n\n```\n\nFor a real world example of syncing a directory of schemas into a directory of matching python typed dictionaries\ncheck out the example app [here](/examples/sync_types)\n\nTo try it out, simply clone this repo and run:\n\n`poetry env use 3.9`\n- This must be done as this library only supports Python 3.9 and above for type generation. You can still use this library in apps that use a lower Python version, as long as Python 3.9 is the active version when the types are generated (either locally or in your CI system).\n\n`poetry install`\n\n`poetry run sync-example`\n\nFor some more advanced examples, like referencing other schema files by their full name take a look at the tests [here](/tests)\n\n### Referencing schemas\n\nThis library supports referencing schemas in different files by their fullname.\n\nIn order for this behaviour to work, all schemas must be in the same directory and use the following naming convention: `namespace.name.avsc`. Note that is the same as `fullname.avsc`\n\nFor more on this checkout the docs for fastavro [here](https://fastavro.readthedocs.io/en/latest/schema.html#fastavro._schema_py.load_schema).\n\nAn example of this can be found in the tests.\n\n### Example output\n\nThe following example shows the type generated for a given schema.\n\n```json\n{\n  "namespace": "example",\n  "type": "record",\n  "name": "User",\n  "fields": [\n    { "name": "name", "type": "string" },\n    { "name": "favorite_number", "type": ["null", "int"] },\n    { "name": "favorite_color", "type": ["null", "string"] },\n    {\n      "name": "address",\n      "type": {\n        "type": "record",\n        "name": "AddressUSRecord",\n        "fields": [\n          { "name": "streetaddress", "type": "string" },\n          { "name": "city", "type": "string" }\n        ]\n      }\n    },\n    {\n      "name": "other_thing",\n      "type": {\n        "type": "record",\n        "name": "OtherThing",\n        "fields": [\n          { "name": "thing1", "type": "string" },\n          { "name": "thing2", "type": ["null", "int"] }\n        ]\n      }\n    }\n  ]\n}\n```\n\n```python\nfrom typing import TypedDict, Optional\n\n# total=False allows us to skip passing optional fields into the constructor\nclass ExampleAddressUSRecord(TypedDict, total=False):\n    streetaddress: str\n    city: str\n\n\nclass ExampleOtherThing(TypedDict, total=False):\n    thing1: str\n    thing2: Optional[int]\n\n\nclass ExampleUser(TypedDict, total=False):\n    name: str\n    favorite_number: Optional[int]\n    favorite_color: Optional[str]\n    address: AddressUSRecord\n    other_thing: OtherThing\n\n```\n\n## Testing\n\nTo run unit tests, run `poetry run pytest`.\n\n## Requirements\n\nPython 3.9 or greater.\n',
    'author': 'Dan Green-Leipciger',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/waveaccounting/avro-to-python-types',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
