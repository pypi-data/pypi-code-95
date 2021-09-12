# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hannah', 'hannah.http', 'hannah.tests']

package_data = \
{'': ['*']}

install_requires = \
['cached-property>=1.5.2,<2.0.0', 'httpx>=0.18.2,<0.19.0']

setup_kwargs = {
    'name': 'hannah',
    'version': '0.0.3',
    'description': '',
    'long_description': "# hannah\n\n`hannah` is a async swagger http client.\n\n## installation\n\n```\npip install hannah\n```\n\n## example\n\n```python\nfrom hannah.http.session import HTTPSession\nfrom hannah.models import SwaggerService\n\nsession = HTTPSession(f'pet-store')\nservice = SwaggerService.from_url('pet-store', 'https://petstore.swagger.io',\n                                  session, swagger_path='/v2/swagger.json')}\nresponse = await service.getPetById(petId=1)\nprint(response)\n```",
    'author': 'suganthsundar',
    'author_email': 'suganthsundar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/suganthsundar/hannah',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
