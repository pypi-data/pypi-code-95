# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qtoml']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.3.0,<22.0']

entry_points = \
{'console_scripts': ['qtoml_testdecode = qtoml.__main__:decode',
                     'qtoml_testencode = qtoml.__main__:encode']}

setup_kwargs = {
    'name': 'qtoml',
    'version': '0.3.1',
    'description': 'New TOML encoder/decoder',
    'long_description': '*****\nqTOML\n*****\n\nqtoml is another Python TOML encoder/decoder. I wrote it because I found\nuiri/toml too unstable, and PyTOML too slow.\n\nFor information concerning the TOML language, see `toml-lang/toml <https://github.com/toml-lang/toml>`_.\n\nqtoml currently supports TOML v0.5.0.\n\nUsage\n=====\n\nqtoml is available on `PyPI <https://pypi.org/project/qtoml/>`_. You can install\nit using pip:\n\n.. code:: bash\n\n  $ pip install qtoml\n\nqtoml supports the standard ``load``/``loads``/``dump``/``dumps`` API common to\nmost similar modules. Usage:\n\n.. code:: pycon\n\n  >>> import qtoml\n  >>> toml_string = """\n  ... test_value = 7\n  ... """\n  >>> qtoml.loads(toml_string)\n  {\'test_value\': 7}\n  >>> print(qtoml.dumps({\'a\': 4, \'b\': 5.0}))\n  a = 4\n  b = 5.0\n  \n  >>> infile = open(\'filename.toml\', \'r\')\n  >>> parsed_structure = qtoml.load(infile)\n  >>> outfile = open(\'new_filename.toml\', \'w\')\n  >>> qtoml.dump(parsed_structure, outfile)\n\nTOML supports a fairly complete subset of the Python data model, but notably\ndoes not include a null or ``None`` value. If you have a large dictionary from\nsomewhere else including ``None`` values, it can occasionally be useful to\nsubstitute them on encode:\n\n.. code:: pycon\n\n  >>> print(qtoml.dumps({ \'none\': None }))\n  qtoml.encoder.TOMLEncodeError: TOML cannot encode None\n  >>> print(qtoml.dumps({ \'none\': None }, encode_none=\'None\'))\n  none = \'None\'\n\nThe ``encode_none`` value must be a replacement encodable by TOML, such as zero\nor a string.\n\nThis breaks reversibility of the encoding, by rendering ``None`` values\nindistinguishable from literal occurrences of whatever sentinel you chose. Thus,\nit should not be used when exact representations are critical.\n\nDevelopment/testing\n===================\n\nqtoml uses the `poetry <https://github.com/sdispater/poetry>`_ tool for project\nmanagement. To check out the project for development, run:\n\n.. code:: bash\n\n  $ git clone --recurse-submodules https://github.com/alethiophile/qtoml\n  $ cd qtoml\n  $ poetry install\n\nThis assumes poetry is already installed. The package and dependencies will be\ninstalled in the currently active virtualenv if there is one, or a\nproject-specific new one created if not.\n\nqtoml is tested against the `alethiophile/toml-test\n<https://github.com/alethiophile/toml-test>`_ test suite, forked from uiri\'s\nfork of the original by BurntSushi. To run the tests, after checking out the\nproject as shown above, enter the ``tests`` directory and run:\n\n.. code:: bash\n\n  $ pytest              # if you already had a virtualenv active\n  $ poetry run pytest   # if you didn\'t\n\nLicense\n=======\n\nThis project is available under the terms of the MIT license.\n',
    'author': 'alethiophile',
    'author_email': 'tomdicksonhunt@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/alethiophile/qtoml',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
