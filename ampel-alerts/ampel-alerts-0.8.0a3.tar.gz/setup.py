# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ampel',
 'ampel.abstract',
 'ampel.alert',
 'ampel.alert.filter',
 'ampel.alert.load',
 'ampel.alert.reject',
 'ampel.dev',
 'ampel.template']

package_data = \
{'': ['*']}

install_requires = \
['ampel-core>=0.8.0-alpha.10,<0.9.0',
 'ampel-interface>=0.8.0-alpha.9,<0.9.0',
 'ampel-photometry>=0.8.0-alpha.1,<0.9.0']

extras_require = \
{':extra == "docs"': ['tomlkit>=0.7.0,<0.8.0'],
 'docs': ['Sphinx>=3.5.1,<5.0.0', 'sphinx-autodoc-typehints>=1.11.1,<2.0.0']}

setup_kwargs = {
    'name': 'ampel-alerts',
    'version': '0.8.0a3',
    'description': 'Alert support for the Ampel system',
    'long_description': '<img align="left" src="https://desycloud.desy.de/index.php/s/mWtE987dgK4NdFc/preview" width="150" height="150"/>  \n<br>\n\n# Alert support for AMPEL\n\n<br><br>\n\nThis add-on enables the processing of `alerts` by AMPEL.\nThe central class of this repository, `ampel.alert.AlertConsumer`,\nis capable of `loading`, `filtering`, `ingesting` these alerts.\n\n- The loading part involves system (or instrument) specific classes.\n- The optional filtering part allows the selection of events based on pre-defined rules. \nHigh-throughput systems, such as ZTF or LSST in astronomy, rely on such filters.\n- The `ingestion` is the step where the content of alerts is saved into the AMPEL database, possibly along with different other documents which can be created according to pre-defined directives.\n\n<p align="center">\n  <img src="https://desycloud.desy.de/index.php/s/fiLRCFZtbTkeCtj/preview" width="40%" />\n  <img src="https://desycloud.desy.de/index.php/s/EBacs5bbApzpwDr/preview" width="40%" />  \n</p>\n\n<p align="center">\n  The <i>AlertConsumer</i> operates on the first three tiers of AMPEL: T0, T1 and T2.\n</p>\n\n\n## Loading Alert \n\nPerformed by subclasses of `ampel.abstract.AbsAlertSupplier`.\n\nConcrete implementation examples: `ampel.ztf.alert.ZiAlertSupplier`\n\nActions break-down:\n\n- Load bytes (tar, network, ...)\n- Deserialize (avro, bson, json, ...)\n- First shape (instrument specific): morph into `AmpelAlert` or `PhotoAlert` Purpose: having a common format that the `AlertConsumer` and alert filters understand. A `PhotoAlert` typically contains two distinct flat sequences, one for photopoints and one for upperlimits. The associated object ID, such as the ZTF name, is converted into nummerical ampel IDs. This is necessary for all alerts (rejected one as well) since "autocomplete" is based on true Ampel IDs.\n\n\n## Filtering Alert \n\nFiltering alerts is performed per channel by subclasses of `ampel.abstract.AbsAlertFilter`.\nAn `AlertConsumer` instance can handle multiple filters.\nAlert filters methods provided by user units are called by the class `FilterBlock`,\nthat handles associated operations (what happens to rejected alerts ? what about auto-complete, etc...) \n`FilterBlock` instances are themselves embedded in `FilterBlocksHandler`\n\nFilters can return:\n  - `False` or `None` to reject an alert.\n  - `True` to accept the alert and create all t1/t2 documents defined in the alert processor directive\n  - An `int` number to accept the alert and create only the t1/t2 documents associated with this group id (as defined in the alert processor directive)\n\n## Ingesting Alert \n\nIf any channel accepts a given alert, DB updates need to occur.\nv0.7 brought many updates regarding how ingestion happens.\nClass: `ampel.alert.ChainedIngestionHandler`, `ampel.abstract.AbsDocIngester`\n\nMore details later\n\n### Directives\nNesting is chaining\n\n### Second shape: morph into `DataPoint`\n\nAlerts that pass any T0 filter are further shaped in order to fullfill\nsome requirements for DB storage and easy later retrieval.\nAmong other things, individual datapoints can be tagged during this step.\nFor ZTF, upper limits do not feature a unique ID, so we have to build our own.\nEach datapoint is shaped into a `ampel.content.DataPoint` structure.\n\nImplementation example: `ampel.ztf.ingest.ZiDataPointShaper`\n\n### Compilers\nOptimize the number of created documents\n\n### Ingesters\nCreate and upserts documents into the DB\n',
    'author': 'Valery Brinnel',
    'author_email': None,
    'maintainer': 'Jakob van Santen',
    'maintainer_email': 'jakob.van.santen@desy.de',
    'url': 'https://ampelproject.github.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
