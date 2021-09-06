import os
import re
from setuptools import setup

__name__ = 'treewalker'

version_fn = os.path.join(__name__, "_version.py")
__version__ = "unknown"
try:
    version_line = open(version_fn, "rt").read()
except EnvironmentError:
    pass  # no version file
else:
    version_regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    m = re.search(version_regex, version_line, re.M)
    if m:
        __version__ = m.group(1)
    else:
        print('unable to find version in {}'.format(version_fn))
        raise RuntimeError('If {} exists, it is required to be well-formed'.format(version_fn))

with open("README.md", "r") as rm:
    long_description = rm.read()

setup(
    name=__name__,
    packages=['treewalker'],
    version=__version__,
    license='MIT',
    description='A simple package to walk a directory tree and collect files and sizes into a SQLite DB.',
    # long description will be the contents of project/README.md
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='BMT Commercial Australia Pty Ltd, Jaap van der Velde',
    author_email='jaap.vandervelde@bmtglobal.com',
    url='https://gitlab.com/bmt-aus/tool/treewalker.git',
    # TODO: update keywords
    keywords=['system', 'tool', 'database'],
    install_requires=['conffu==2.2.16', 'scandir', 'typing'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts': ['treewalker=treewalker.treewalker:cli_entry_point'],
    }
)
