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
    'version': '0.1.0a3',
    'description': 'A library for contract-testing OpenAPI / Swagger APIs.',
    'long_description': '\n===================================================\nOpenApiDriver for Robot Framework®\n===================================================\n\nOpenDriver is an extension of the Robot Framework® DataDriver library that allows for\ngeneration and execution of test cases based on the information in an OpenAPI document\n(also known as Swagger document).\nThis document explains how to use the OpenApiDriver library.\n\nFor more information about Robot Framework®, see http://robotframework.org.\nFor more information about the DataDriver library, see\nhttps://github.com/Snooz82/robotframework-datadriver.\n\n\nInstallation\n------------\n\nIf you already have Python >= 3.8 with pip installed, you can simply run:\n\n``pip install --upgrade robotframework-openapidriver``\n\nOpenAPI (aka Swagger)\n~~~~~~~~~~~~~~~~~~~~~\n\nThe OpenAPI Specification (OAS) defines a standard, language-agnostic interface to RESTful APIs.\nhttps://swagger.io/specification/\n\nThe openapi module implements a reader class that generates a test case for each\nendpoint, method and response that is defined in an OpenAPI document, typically\nan openapi.json or openapi.yaml file.\n\n\nHow it works\n^^^^^^^^^^^^\n\nIf the source file has the .json or .yaml extension, it will be\nloaded by the prance module and the test cases will be generated.\n\n.. code :: robotframework\n\n    *** Settings ***\n    Library            OpenApiDriver\n    ...                    source=openapi.json\n    Test Template      Do Nothing\n\n\n    *** Test Cases ***\n    Some OpenAPI test for ${method} on ${endpoint} where ${status_code} is expected\n\n    *** Keywords *** ***\n    Do Nothing\n        [Arguments]    ${endpoint}    ${method}    ${status_code}\n        No Operation\n\nIt is also possible to load the openapi.json / openapi.yaml directly from the server\nby using the url instead of a local file:\n\n.. code :: robotframework\n\n    *** Settings ***\n    Library            OpenApiDriver\n    ...                    source=http://127.0.0.1:8000/openapi.json\n\n\nSince the OpenAPI document is essentially a contract that specifies what operations are\nsupported and what data needs to be send and will be returned, it is possible to\nautomatically validate the API against this contract. For this purpose, the openapi\nmodule also implements a number of keywords.\n\n',
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
