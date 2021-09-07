# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hko']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'hko',
    'version': '0.1.2',
    'description': 'An unofficial Python wrapper for public API of Hong Kong Observatory',
    'long_description': '[![GitHub Release][releases-shield]][releases]\n[![PyPI][pypi-releases-shield]][pypi-releases]\n\n# python-hko\nA python warpper for getting Hong Kong SAR local weather from Hong Kong Observatory Open Data API.\nPlease refer to the Official Documentation for request parameters and response details.\n[Official API Documentation][hko-documentation]\n\n## Reference\n### HKO Module\n`hko.HKO(websession)`\nManage and perform requests\nReturn: hko.HKO class\n\nParameter | Optional | Type | Description\n--- | --- | --- | ---\nwebsession | no | ClientSession | see [aiphttp](https://docs.aiohttp.org/en/stable/client_reference.html)\n\n`hko.HKO.weather(type, lang="en")`\nRetrieve weather data from Weather Information API\nReturn: dictionary\n\nParameter | Optional | Type | Description | Accepted values\n--- | --- | --- | --- | ---\ndataType | no | string | type of data requested | see [Official API Documentation][hko-documentation]\nlang | yes | string| language used in response | see [Official API Documentation][hko-documentation]\n\n## Usage Example\nGet and print local weather forcast general situation in English\n```python\nfrom hko import HKO\nimport asyncio\nfrom aiohttp import ClientSession, ClientResponse\nfrom aiohttp import ClientConnectorError\n\nasync def main():\n    async with ClientSession() as websession:\n        try:\n            hko = HKO(websession)\n            fnd = await hko.weather("fnd")\n            print(fnd["generalSituation"])\n        except ClientConnectorError as error:\n            print(error)\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(main())\nloop.close()\n```\n\n\n\n\n\n[hko-documentation]: https://www.hko.gov.hk/en/weatherAPI/doc/files/HKO_Open_Data_API_Documentation.pdf\n[releases]: https://github.com/MisterCommand/python-hko\n[releases-shield]: https://img.shields.io/github/release/MisterCommand/python-hko.svg?style=popout\n[pypi-releases]: https://pypi.org/project/hko/\n[pypi-releases-shield]: https://img.shields.io/pypi/v/hko',
    'author': 'MisterCommand',
    'author_email': 'anthonyhou04@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MisterCommand/python-hko',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
