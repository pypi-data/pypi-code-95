# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['airnow']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.2,<3.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'python-airnow',
    'version': '0.1.1',
    'description': 'A simple wrapper around the AirNow API',
    'long_description': "[![CI](https://github.com/ronnie-llamado/python-airnow/actions/workflows/ci.yml/badge.svg)](https://github.com/ronnie-llamado/python-airnow/actions/workflows/ci.yml)\n[![codecov](https://codecov.io/gh/ronnie-llamado/python-airnow/branch/main/graph/badge.svg?token=KJZNDU1Z6Q)](https://codecov.io/gh/ronnie-llamado/python-airnow)\n[![Documentation Status](https://readthedocs.org/projects/python-airnow/badge/?version=latest)](https://python-airnow.readthedocs.io/en/latest/?badge=latest)\n# python-airnow\nA simple wrapper around [AirNow API](https://docs.airnowapi.org/).\n\n## Install\n\n```\npip install -U python-airnow\n```\n\n## Example\n\n```python\nimport airnow\n\nAIRNOW_API_KEY = '{INSERT_API_KEY}'\nair = airnow.AirNow(AIRNOW_API_KEY)\n\nobsrvtns = air.getObservationsByZipCode(20002)\nprint(obsrvtns)\n# [\n#     AirNowObservation(\n#         DateTime=datetime.datetime(2021, 9, 7, 12, 0, tzinfo=tzoffset('EST', -18000)),\n#         ReportingArea='Metropolitan Washington',\n#         ParameterName='O3',\n#         AQI=46\n#     ),\n#     AirNowObservation(\n#         DateTime=datetime.datetime(2021, 9, 7, 12, 0, tzinfo=tzoffset('EST', -18000)),\n#         ReportingArea='Metropolitan Washington',\n#         ParameterName='PM2.5',\n#         AQI=4\n#     )\n# ]\n\nfrcst = air.getForecastByLatLong(38.919, -77.013, date=datetime.datetime(2021,9,7))\nprint(frcst)\n# [\n#     AirNowForecast(\n#       DateForecast=datetime.date(2021, 9, 7),\n#       ReportingArea='Metropolitan Washington',\n#       ParameterName='O3',\n#       AQI=61\n#     ),\n#     AirNowForecast(\n#       DateForecast=datetime.date(2021, 9, 7),\n#       ReportingArea='Metropolitan Washington',\n#       ParameterName='PM2.5',\n#       AQI=38),\n#     AirNowForecast(\n#       DateForecast=datetime.date(2021, 9, 8),\n#       ReportingArea='Metropolitan Washington',\n#       ParameterName='O3',\n#       AQI=50\n#     ),\n#     AirNowForecast(\n#       DateForecast=datetime.date(2021, 9, 8),\n#       ReportingArea='Metropolitan Washington',\n#       ParameterName='PM2.5',\n#       AQI=46\n#     ),\n#     AirNowForecast(\n#       DateForecast=datetime.date(2021, 9, 9),\n#       ReportingArea='Metropolitan Washington',\n#       ParameterName='O3',\n#       AQI=46\n#     ),\n#     AirNowForecast(\n#       DateForecast=datetime.date(2021, 9, 9),\n#       ReportingArea='Metropolitan Washington',\n#       ParameterName='PM2.5',\n#       AQI=33\n#     )\n# ]\n\n```\n\n## Links\n- Documentation: https://python-airnow.readthedocs.io/\n- PyPI Releases: https://pypi.org/project/python-airnow/\n- Source Code: https://github.com/ronnie-llamado/python-airnow/\n- Issue Tracker: https://github.com/ronnie-llamado/python-airnow/issues/\n- AirNow API Documentation: https://docs.airnowapi.org\n",
    'author': 'Ronnie Llamado',
    'author_email': 'llamado.ronnie@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
