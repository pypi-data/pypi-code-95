# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datamask']

package_data = \
{'': ['*']}

install_requires = \
['Faker>8.12.0', 'psycopg2-binary>2.8.0,<2.10', 'python-slugify>4.0.0,<6.0.0']

entry_points = \
{'console_scripts': ['datadict = datamask.datadict:main',
                     'datamask = datamask.cleaner:main']}

setup_kwargs = {
    'name': 'datamask',
    'version': '1.0.3',
    'description': 'Data PII cleaning/masking for databases',
    'long_description': '# pgdatacleaner\n## Purpose\nMask sensetive data in a database (i.e. PII/PHI) so it can be used for development/testing purposes. \nIt is meant to keep IDs, so databases that for some reason has PII data in PK/FKs won\'t work very well.\n## Usage\nFirst, create a data dictionary from an existing database:\n```bash\ndatadict \'postgresql://<user>:<password>@<host>/<database>\' <schema> my_pii_dd.csv \n```\nYou will need to edit this file and set `pii` to `yes` for any columns that need to be masked,\nand the `pii_type` to one of the available types to generate fake data. `dataclean -h` will \nlist all available fakers.\n\nThen, run `dataclean` to modify a database masking data as specified in the CSV. This is not a very fast operation\non databases of any significant size.\n```bash\ndataclean -f \'postgresql://<user>:<password>@<host>/<database>\' -f my_edited_pii_dd.csv \n```\n\nIf you change your schema, adding/modifying/deleting columns and tables, you can regenerate the data dictionary\nusing your last copy as a seed so you don\'t have to re-specify columns that have not changed:\n\n```bash\ndatadict \'postgresql://<user>:<password>@<host>/<database>\' <schema> -i my_existing_dd.csv my_new_pii_dd.csv \n```\n\n## Status\nUnstable, alpha, consisting of 50% todo\'s and hacks, but working. \n\n## Caveats\nI\'m not responsible for your data. Never run this against a production database, unless you feel like testing your backup restore procedures.\n\n## License\n\nCopyright (c) 2021, Fredrik Håård\n\nDo whatever you want, don\'t blame me. You may also use this software as licensed under the MIT or BSD licenses, or the more permissive license below:\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n',
    'author': 'Fredrik Håård',
    'author_email': 'fredrik@metallapan.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/haard/datamask',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
