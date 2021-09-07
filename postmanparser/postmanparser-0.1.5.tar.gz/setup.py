# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['postmanparser']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.18.1,<0.19.0']

setup_kwargs = {
    'name': 'postmanparser',
    'version': '0.1.5',
    'description': 'Postman collection parser for python',
    'long_description': '# postmanparser\n![Build](https://github.com/appknox/postmanparser/actions/workflows/test.yml/badge.svg)\n[![codecov](https://codecov.io/gh/appknox/postmanparser/branch/main/graph/badge.svg?token=BXCg5XODJw)](https://codecov.io/gh/appknox/postmanparser)\n\n## Introduction\n\nPostman collection parser written in python3 to extract HTTP requests/responses.\nCurrently supports reading JSON schema two ways\n- Read from `.json` file\n- Fetch from url where schema is exposed\n\n## Installation\n - Using pip\n\n        pip install postmanparser\n\n- Using poetry\n\n        poetry add postmanparser\n\n## Getting Started\n\n### Parsing API Schema\nYou can parse API schema from file or from url as below.\n- From file\n\n```python\nfrom postmanparser import Collection\ncollection = Collection()\ncollection.parse_from_file("path/to/postman/schema.json")\n```\n\n- From url\n\n```python\nfrom postmanparser import Collection\ncollection = Collection()\ncollection.parse_from_url("http://example.com/schema")\n```\nURL should be a `GET` request.\n\npostmanparser also validates for the required fields mentioned by postman schema documentation which is available at https://schema.postman.com/\n\n### Reading the data\nPostman collection contains group of requests and one or more folders having group of requests and/or nested folders in it.\n\n#### Getting requests from the collection\n\nYou can retreive all the requests present in the collection using `get_requests()` method.\nThis method will recursively search for the requests inside folders is present.\n\n```python\ncollection = Collection()\ncollection.parse_from_file("path/to/postman/schema.json")\nrequests = collection.get_requests()\nfor request in requests:\n        print(request) #Either a Request object or str\n```\n\nYou can retrieve the requests inside specific folder by using `folder="folder_name"` in `get_requests` method. To get requests from the nested folder, use folder path separated by `/`\n\nFor e.g. to get requests inside folder2 which is nested in folder1\n```python\nrequests = collection.get_requests(folder="folder/sub_folder")\n```\n\nYou can pass `recursive=False` to `get_requests()` if you don\'t want to do recusrive lookup. In this case\nyou will get all the requests present at the root level of collection or at the folder level is folder is specified.\n\n```python\nrequests = collection.get_requests(recursive=False)\n```\n\n#### Getting requests mapped by folder in the collection\nYou can access requests in the collections as requests map using `get_requests_map()`. The key of the dict is path to the folder separated by backlash and value is list of requests of type `Request` or `str`.\nThis will be recursive search for all the folders and sub folders inside it.\n\n```python\ncollection = Collection()\ncollection.parse_from_file("path/to/postman/schema.json")\nrequests = collection.get_requests_map()\nrequests = collection.get_requests_map(folder="folder/sub_folder")\n```\n\n### Validation\nIf schema found to be invalid following exception will be thrown.\n- `MissingRequiredFieldException`\n- `InvalidPropertyValueException`\n- `InvalidObjectException`\n- `FolderNotFoundException`\n\n## Schema Support\npostmanparser is still in early stages and will be updated with missing schema components soon.\n\nFollowing are the objects which are not supported yet but will be added in the future.\n- protocolProfileBehavior\n\n## Collection SDK Compatibility\n\nCurrently postmanparser is not aligned with collection SDK node module. http://www.postmanlabs.com/postman-collection/\n\nThis Might be added in future. Feel free to raise the PR.\n\n\n## Version Compatibility\npostmanparser supports collection schema v2.0.0 and v2.1.0.',
    'author': 'Appknox',
    'author_email': 'engineering@appknox.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/appknox/postmanparser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
