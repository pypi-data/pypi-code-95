# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['openapidriver']

package_data = \
{'': ['*']}

install_requires = \
['openapi-core',
 'openapi-spec-validator',
 'prance',
 'requests',
 'robotframework-datadriver>=1.5',
 'robotframework-pythonlibcore>=3',
 'robotframework>=4']

setup_kwargs = {
    'name': 'robotframework-openapidriver',
    'version': '0.1.0a6',
    'description': 'A library for contract-testing OpenAPI / Swagger APIs.',
    'long_description': '\n# OpenApiDriver for Robot Framework®\n\nOpenApiDriver is an extension of the Robot Framework® DataDriver library that allows\nfor generation and execution of test cases based on the information in an OpenAPI\ndocument (also known as Swagger document).\nThis document explains how to use the OpenApiDriver library.\n\nFor more information about Robot Framework®, see http://robotframework.org.\n\nFor more information about the DataDriver library, see\nhttps://github.com/Snooz82/robotframework-datadriver.\n\n---\n> Note: OpenApiDriver is currently in early development so there are currently\nrestrictions / limitations that you may encounter when using this library to run\ntests against an API. See [Limitations](#limitations) for details.\n\n---\n## Installation\n\nIf you already have Python >= 3.8 with pip installed, you can simply run:\n\n``pip install --upgrade robotframework-openapidriver``\n\n---\n## OpenAPI (aka Swagger)\n\nThe OpenAPI Specification (OAS) defines a standard, language-agnostic interface\nto RESTful APIs, see https://swagger.io/specification/\n\nThe OpenApiDriver module implements a reader class that generates a test case for\neach endpoint, method and response that is defined in an OpenAPI document, typically\nan openapi.json or openapi.yaml file.\n\n---\n## How it works\n\nIf the source file has the .json or .yaml extension, it will be loaded by the\nlibrary (using the prance library under the hood) and the test cases will be generated.\n\n``` code robotframework\n*** Settings ***\nLibrary            OpenApiDriver\n...                    source=openapi.json\nTest Template      Do Nothing\n\n\n*** Test Cases ***\nSome OpenAPI test for ${method} on ${endpoint} where ${status_code} is expected\n\n*** Keywords *** ***\nDo Nothing\n    [Arguments]    ${endpoint}    ${method}    ${status_code}\n    No Operation\n```\n\nIt is also possible to load the openapi.json / openapi.yaml directly from the\nserver by using the url instead of a local file:\n\n``` code robotframework\n*** Settings ***\nLibrary            OpenApiDriver\n...                    source=http://127.0.0.1:8000/openapi.json\n```\n\nSince the OpenAPI document is essentially a contract that specifies what operations are\nsupported and what data needs to be send and will be returned, it is possible to\nautomatically validate the API against this contract. For this purpose, the openapi\nmodule also implements a number of keywords.\n\nMost of these keywords are for internal use by the library (for example to ensure the\nresult logs provide insight into the executed steps) but a number of them are intended\nto be used as ``Test Template`` or within the ``Keyword`` that serves as the\n``Test Template``.\n\n---\n## Limitations\n\nThere are currently a number of limitations to supported API structures, supported\ndata types and properties. The following list details the most important ones:\n- Only JSON request and response bodies are currently supported.\n- The unique identifier for a resource as used in the ``paths`` section of the\n    openapi document is expected to be the ``id`` property on a resource of that type.\n- The ``id`` is expected to be a UUID (v4).\n- No support for query strings at this time.\n- No support for headers.\n- Limited support for authentication\n    - ``username`` and ``password`` can be passed as parameters to use Basic Authentication\n    - A [requests AuthBase instance](https://docs.python-requests.org/en/latest/api/#authentication)\n        can be passed and it will be used as provided.\n    - No support for per-endpoint authorization levels (just simple 401 validation).\n- ``exclusiveMinimum`` and ``exclusiveMaximum`` not supported yet.\n- byte, binary, date, date-time string formats not supported yet.\n\n',
    'author': 'Robin Mackaij',
    'author_email': None,
    'maintainer': 'Robin Mackaij',
    'maintainer_email': None,
    'url': 'https://github.com/MarketSquare/robotframework-openapidriver',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
