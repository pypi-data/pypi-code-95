# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xray']

package_data = \
{'': ['*']}

install_requires = \
['PyMuPDF>=1.18.17,<2.0.0']

setup_kwargs = {
    'name': 'x-ray',
    'version': '0.2.0',
    'description': 'A library and microservice to find bad redactions in PDFs',
    'long_description': '![Image of REDACTED STAMP](https://raw.githubusercontent.com/freelawproject/x-ray/main/redacted.png)\n\nx-ray is a Python library for finding bad redactions in PDF documents.\n\n## Why?\n\nAt Free Law Project, we collect millions of PDFs each day. An ongoing problem\nis that people fail to properly redact things. Instead of doing it the right\nway, they just draw a black rectangle or a black highlight on top of black\ntext and call it a day. Well, when that happens you just select the text under\nthe rectangle, and you can read it again. Not great.\n\nAfter witnessing this problem for years, we decided it would be good to figure\nout how common it is, so, with some help, we built this simple tool. You give\nthe tool the path to a PDF. It tells you if it has worthless redactions in it.\n\n\n## What next?\n\nRight now, `x-ray` works pretty well and we are using it to analyze documents\nin our collections. It could be better though. Bad redactions take many forms.\nSee the issues tab for other examples we don\'t yet support. We\'d love your\nhelp solving some of tougher cases.\n\n\n## Installation\n\nWith poetry, do:\n\n```text\npoetry add x-ray\n```\n\nWith pip, that\'d be:\n```text\npip install x-ray\n```\n\n## Usage\n\nYou can easily use this on the command line. Once installed, just:\n\n```bash\n% python -m xray path/to/your/file.pdf\n{\n  "1": [\n    {\n      "bbox": [\n        58.550079345703125,\n        72.19873046875,\n        75.65007781982422,\n        739.3987426757812\n      ],\n      "text": "The Ring travels by way of Cirith Ungol"\n    }\n  ]\n}\n```\n\nThat\'ll give you json, so you can use it with tools like [`jq`][jq]. The format is as follows:\n\n - It\'s a dict.\n - The keys are page numbers.\n - Each page number maps to a list of dicts.\n - Each of those dicts maps to two keys.\n - The first key is `bbox`. This is a four-tuple that indicates the x,y positions of the upper left corner and then lower right corners of the bad redaction.\n - The second key is `text`. This is the text under the bad rectangle.\n\nSimple enough.\n\nIf you want a bit more, you can use `x-ray` in Python:\n\n```python\nfrom pprint import pprint\nimport xray\nbad_redactions = xray.inspect("some/path/to/your/file.pdf")\npprint(bad_redactions)\n{1: [{\'bbox\': (58.550079345703125,\n               72.19873046875,\n               75.65007781982422,\n               739.3987426757812),\n      \'text\': \'Aragorn is the one true king.\'}]}\n```\n\nThe output is the same as above, except it\'s a Python object, not a JSON object.\n\nIf you already have the file contents as a `bytes` object, that\'ll work too:\n\n```python\nsome_bytes = requests.get("https://lotr-secrets.com/some-doc.pdf").content\nbad_redactions = xray.inspect(some_bytes)\n```\n\nNote that because the `inspect` method uses the same signature no matter what,\nthe type of the object you give it is essential. So if you do this, `xray` will\nassume your file name (provided as bytes) is file contents and it won\'t work:\n\n```python\nxray.inspect(b"some-file-path.pdf")\n```\n\nThat\'s pretty much it. There are no configuration files or other variables to\nlearn. You give it a file name. If there is a bad redaction in it, you\'ll soon\nfind out.\n\n\n## How it works\n\nUnder the covers, `x-ray` uses the high-performant [PyMuPDF project][mu] to parse PDFs.\n\nYou can read the source to see how it works, but the general idea is to:\n\n1. Find rectangles in the PDF.\n\n2. Find letters that are under those rectangles.\n\nThings get tricky in a couple places:\n\n - letters without [ascenders][asc] are taller than they seem and might not be entirely under the rectangle\n - drawings in PDFs can contain multiple rectangles\n - text under redactions can be on purpose (like if it says "XXX" or "privileged", etc)\n\nAnd so forth. We do our best.\n\n\n## Contributions\n\nPlease see the issues list for thinsg we need, or start a conversation if you have questions. Before you do your first contribution, we\'ll need a signed contributor license agreement. See the template in the repo.\n\n\n## Deployment\n\nReleases happen automatically via Github Actions on any commit that is tagged with something like "v0.0.0".\n\nIf you wish to create a new version manually, the process is:\n\n1. Update version info in `pyproject.toml`\n\n2. Configure your Pypi credentials [with Poetry][creds]\n\n3. Build and publish the version:\n\n```sh\npoetry publish --build\n```\n\n\n\n## License\n\nThis repository is available under the permissive BSD license, making it easy and safe to incorporate in your own libraries.\n\nPull and feature requests welcome. Online editing in GitHub is possible (and easy!).\n\n[jq]: https://stedolan.github.io/jq/\n[mu]: pymupdf.readthedocs.io/\n[asc]: https://en.wikipedia.org/wiki/Ascender_(typography)\n[creds]: https://python-poetry.org/docs/repositories/#configuring-credentials\n',
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
