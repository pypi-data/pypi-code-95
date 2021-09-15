"""fbs tutorial helper for Mac

See:
https://github.com/mherrmann/fbs-tutorial-shim-mac
"""

from os.path import relpath, join
from setuptools import setup, find_packages

import os

def _get_package_data(pkg_dir, data_subdir):
    result = []
    for dirpath, _, filenames in os.walk(join(pkg_dir, data_subdir)):
        for filename in filenames:
            filepath = join(dirpath, filename)
            result.append(relpath(filepath, pkg_dir))
    return result

description = 'fbs tutorial helper for Mac'
setup(
    name='fbs-tutorial-shim-mac',
    version='1.0.1',
    description=description,
    long_description=
        description + '\n\nSee: https://github.com/mherrmann/fbs-tutorial-shim-mac',
    author='Michael Herrmann',
    author_email='michael+removethisifyouarehuman@herrmann.io',
    url='https://github.com/mherrmann/fbs-tutorial-shim-mac',
    packages=find_packages(),
    package_data={
        'fbs_tutorial_shim_mac': \
            _get_package_data('fbs_tutorial_shim_mac', 'data')
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    
        'Operating System :: MacOS',
    
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',

        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    license='GPLv3 or later',
    keywords='PyQt',
    platforms=['Mac']
)
