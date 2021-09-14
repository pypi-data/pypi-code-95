# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['x_ray']

package_data = \
{'': ['*']}

install_requires = \
['PyMuPDF>=1.18.17,<2.0.0']

setup_kwargs = {
    'name': 'x-ray',
    'version': '0.0.1',
    'description': 'A library and microservice to find bad redactions in PDFs',
    'long_description': '![Image of REDACTED STAMP](https://github.com/freelawproject/pdf-redaction-detector/blob/master/Screenshot%20from%202020-12-17%2011-06-09.png)\n\nx-ray is a Python 3.8 library for finding bad redactions in PDF documents.\n\n# Why this exists\n\nXXX\n\n# Installation\n\nWith poetry, do:\n\n```text\npoetry add x-ray\n```\n\nWith pip, that\'d be:\n```text\npip install x-ray\n```\n\n# Usage\n\nYou can easily use this on the command line. Once installed, just:\n\n```bash\n% python -m xray path/to/your/file.pdf\n{\n  "1": [\n    {\n      "bbox": [\n        58.550079345703125,\n        72.19873046875,\n        75.65007781982422,\n        739.3987426757812\n      ],\n      "text": "12345678910111213141516171819202122232425262728"\n    }\n  ]\n}\n```\n\nThat\'ll give you json, so you can use it with tools like [`jq`][jq]. Handy.\n\nIf you want a bit more, you can use it in Python:\n\n```python\nfrom pprint import pprint\nimport xray\nbad_redactions = xray.inspect("some/path/to/your/file.pdf")\npprint(bad_redactions)\n{1: [{\'bbox\': (58.550079345703125,\n               72.19873046875,\n               75.65007781982422,\n               739.3987426757812),\n      \'text\': \'12345678910111213141516171819202122232425262728\'}]}\n```\n\nThat\'s pretty much it. There are no configuration files or other variables to\nlearn. You give it a file name. If there is a bad redaction in it, you\'ll soon\nfind out.\n\n# How it works\n\n{{NEW-PROJECT}} is an open source repository to ...\nIt was built for use with Courtlistener.com.\n\nIts main goal is to ...\nIt incldues mechanisms to ...\n\nFurther development is intended and all contributors, corrections and additions are welcome.\n\n## Background\n\nFree Law Project built this ...  This project represents ...  \nWe believe to be the ....\n\n\n## Fields\n\n1. `id` ==> string; Courtlistener Court Identifier\n2. `court_url` ==> string; url for court website\n3. `regex` ==>  array; regexes patterns to find courts\n\n\n## Installation\n\nInstalling {{NEW-PROJECT}} is easy.\n\n```sh\npip install {{NEW-PROJECT}}\n```\n\n\nOr install the latest dev version from github\n\n```sh\npip install git+https://github.com/freelawproject/{{NEW-PROJECT}}.git@master\n```\n\n## Future\n\n1) Continue to improve ...\n2) Future updates\n\n## Deployment\n\nIf you wish to create a new version manually, the process is:\n\n1. Update version info in `setup.py`\n\n2. Install the requirements using `poetry install`\n\n3. Set up a config file at `~/.pypirc`\n\n4. Generate a universal distribution that works in py2 and py3 (see setup.cfg)\n\n```sh\npython setup.py sdist bdist_wheel\n```\n\n5. Upload the distributions\n\n```sh\ntwine upload dist/* -r pypi (or pypitest)\n```\n\n## License\n\nThis repository is available under the permissive BSD license, making it easy and safe to incorporate in your own libraries.\n\nPull and feature requests welcome. Online editing in GitHub is possible (and easy!)\n\n[jq]: https://stedolan.github.io/jq/\n',
    'author': 'Free Law Project',
    'author_email': 'info@free.law',
    'maintainer': 'Free Law Project',
    'maintainer_email': 'info@free.law',
    'url': 'https://github.com/freelawproject/pdf-redaction-detector',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
