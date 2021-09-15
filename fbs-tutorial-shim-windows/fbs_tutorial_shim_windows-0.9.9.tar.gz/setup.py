"""fbs tutorial helper on Windows

See:
https://github.com/mherrmann/fbs-tutorial-shim-windows
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

description = 'Create cross-platform desktop applications with Python and Qt'
setup(
    name='fbs_tutorial_shim_windows',
    version='0.9.9',
    description=description,
    long_description=
        description + '\n\nSee: https://github.com/mherrmann/fbs-tutorial-shim-windows',
    author='Michael Herrmann',
    author_email='michael+removethisifyouarehuman@herrmann.io',
    url='https://github.com/mherrmann/fbs-tutorial-shim-windows',
    package_data={
        'fbs_tutorial_shim_windows': \
            _get_package_data('fbs_tutorial_shim_windows', 'data')
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    
        'Operating System :: Microsoft :: Windows',
    
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
    platforms=['Windows']
)