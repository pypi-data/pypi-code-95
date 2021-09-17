# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['airnow']

package_data = \
{'': ['*']}

install_requires = \
['Shapely>=1.7.1,<2.0.0',
 'geopandas>=0.9.0,<0.10.0',
 'pyhumps>=3.0.2,<4.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'python-airnow',
    'version': '1.0.0a0',
    'description': 'A simple wrapper around the AirNow API',
    'long_description': "![PyPI](https://img.shields.io/pypi/v/python-airnow)\n[![CI](https://github.com/ronnie-llamado/python-airnow/actions/workflows/ci.yaml/badge.svg)](https://github.com/ronnie-llamado/python-airnow/actions/workflows/ci.yaml)\n[![codecov](https://codecov.io/gh/ronnie-llamado/python-airnow/branch/main/graph/badge.svg?token=KJZNDU1Z6Q)](https://codecov.io/gh/ronnie-llamado/python-airnow)\n[![Documentation Status](https://readthedocs.org/projects/python-airnow/badge/?version=latest)](https://python-airnow.readthedocs.io/en/latest/?badge=latest)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/python-airnow)\n# python-airnow\nA wrapper around [AirNow API](https://docs.airnowapi.org/).\n\n## Install\n\n```\npip install -U python-airnow\n```\n\n## Example\n\n```python\nimport airnow\nimport datetime\n\nAIRNOW_API_KEY = '{INSERT_API_KEY}'\nair = airnow.AirNow(AIRNOW_API_KEY)\n\nobsrvtns = air.observation.by_zip_code(20002)\nprint(obsrvtns)\n# [\n#     AirNowObservation(\n#         date_time=datetime.datetime(2021, 9, 7, 12, 0, tzinfo=tzoffset('EST', -18000)),\n#         reporting_area='Metropolitan Washington',\n#         parameter_name='O3',\n#         aqi=46\n#     ),\n#     AirNowObservation(\n#         date_time=datetime.datetime(2021, 9, 7, 12, 0, tzinfo=tzoffset('EST', -18000)),\n#         reporting_area='Metropolitan Washington',\n#         parameter_name='PM2.5',\n#         aqi=4\n#     )\n# ]\n\nfrcst = air.forecast.by_lat_long(38.919, -77.013, date=datetime.datetime(2021,9,7))\nprint(frcst)\n# [\n#     AirNowForecast(\n#       date_forecast=datetime.date(2021, 9, 7),\n#       reporting_area='Metropolitan Washington',\n#       parameter_name='O3',\n#       aqi=61\n#     ),\n#     AirNowForecast(\n#       date_forecast=datetime.date(2021, 9, 7),\n#       reporting_area='Metropolitan Washington',\n#       parameter_name='PM2.5',\n#       aqi=38),\n#     AirNowForecast(\n#       date_forecast=datetime.date(2021, 9, 8),\n#       reporting_area='Metropolitan Washington',\n#       parameter_name='O3',\n#       aqi=50\n#     ),\n#     AirNowForecast(\n#       date_forecast=datetime.date(2021, 9, 8),\n#       reporting_area='Metropolitan Washington',\n#       parameter_name='PM2.5',\n#       aqi=46\n#     ),\n#     AirNowForecast(\n#       date_forecast=datetime.date(2021, 9, 9),\n#       reporting_area='Metropolitan Washington',\n#       parameter_name='O3',\n#       aqi=46\n#     ),\n#     AirNowForecast(\n#       date_forecast=datetime.date(2021, 9, 9),\n#       reporting_area='Metropolitan Washington',\n#       parameter_name='PM2.5',\n#       aqi=33\n#     )\n# ]\n\n```\n\n## Links\n- Documentation: https://python-airnow.readthedocs.io/\n- PyPI Releases: https://pypi.org/project/python-airnow/\n- Source Code: https://github.com/ronnie-llamado/python-airnow/\n- Issue Tracker: https://github.com/ronnie-llamado/python-airnow/issues/\n- AirNow API Documentation: https://docs.airnowapi.org\n",
    'author': 'Ronnie Llamado',
    'author_email': 'llamado.ronnie@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
