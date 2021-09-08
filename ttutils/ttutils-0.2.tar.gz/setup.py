import re
import os
import pathlib
from setuptools import setup


try:
    version = re.findall(r"^__version__ = '([^']+)'\r?$",
        (pathlib.Path(__file__).parent / 'ttutils' / '__init__.py').read_text('utf-8'), re.M)[0]
except IndexError:
    raise RuntimeError('Unable to determine version.')


def read(filename):
    with open(os.path.join(filename), 'rt') as f:
        return f.read().strip()


setup(
    version=version,
    packages=['ttutils'],
    long_description=read('README.rst'),
    include_package_data=True,
    install_requires=[
        'PyYaml',
    ],

    setup_requires=["pytest-runner"],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-flake8',
        'flake8-print',
        'flake8-blind-except==0.1.1',
        'flake8-builtins==1.4.1',
    ]
)
