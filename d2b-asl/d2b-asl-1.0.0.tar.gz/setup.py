# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['d2b_asl']
install_requires = \
['d2b>=1.1.4,<2.0.0']

entry_points = \
{'d2b': ['asl = d2b_asl']}

setup_kwargs = {
    'name': 'd2b-asl',
    'version': '1.0.0',
    'description': 'Plugin for the d2b package to handle ASL data',
    'long_description': '# d2b-asl\n\nPlugin for the d2b package to handle ASL data\n\n[![PyPI Version](https://img.shields.io/pypi/v/d2b-asl.svg)](https://pypi.org/project/d2b-asl/)\n\n## Installation\n\n```bash\npip install d2b-asl\n```\n\n## User Guide\n\nThis package adds support for the `aslContext` field in the description objects located in the `d2b` config files. This field should be an array of strings, where each string is a volume type (as defined in the [BIDS specification here](https://bids-specification.readthedocs.io/en/v1.6.0/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#_aslcontexttsv)). Specifically, this array should have the same number of entries as the described ASL acquisition has volumes (if there are 109 volumes in the acquisition which this description is describing, then `aslContext` should be an array of length 109).\n\nFor example, a config file describing an ASL acquisition might looks something like:\n\n```json\n{\n  "descriptions": [\n    {\n      "dataType": "perf",\n      "modalityLabel": "asl",\n      "criteria": {\n        "ProtocolName": "ep2d_pasl",\n        "MagneticFieldStrength": 3,\n        "MRAcquisitionType": "2D",\n        "ImageType": [\n          "ORIGINAL",\n          "PRIMARY",\n          "ASL",\n          "NONE",\n          "ND",\n          "NORM",\n          "FILTERED",\n          "MOSAIC"\n        ]\n      },\n      "sidecarChanges": {\n        "ArterialSpinLabelingType": "PASL",\n        "PostLabelingDelay": 1.8,\n        "BackgroundSuppression": false,\n        "M0Type": "Included",\n        "TotalAcquiredPairs": 54,\n        "AcquisitionVoxelSize": [3.5, 3.5, 4.5],\n        "BolusCutOffFlag": true,\n        "BolusCutOffDelayTime": 0.7,\n        "BolusCutOffTechnique": "Q2TIPS",\n        "PASLType": "PICORE"\n      },\n      "aslContext": [\n        "m0scan",\n        "control",\n        "label",\n        "control",\n        "label",\n        "control",\n        "label",\n        // full array omitted for readability ...\n        "control",\n        "label"\n      ]\n    }\n  ]\n}\n```\n',
    'author': 'Andrew Ross',
    'author_email': 'andrew.ross.mail@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/d2b-dev/d2b-asl',
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
