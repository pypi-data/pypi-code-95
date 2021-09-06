#!/usr/bin/env python
#   -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'meed',
        version = '0.0.2',
        description = 'A configurable stats logger for the end user',
        long_description = '',
        long_description_content_type = None,
        classifiers = [
            'Intended Audience :: Customer Service',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.9'
        ],
        keywords = '',

        author = 'Tristan Arthur',
        author_email = 'tristanarthur@pm.me',
        maintainer = '',
        maintainer_email = '',

        license = 'Apache Software License',

        url = '',
        project_urls = {},

        scripts = ['scripts/meed.py'],
        packages = ['meedlib'],
        namespace_packages = [],
        py_modules = [],
        entry_points = {
            'console_scripts': ['meed=meed:main']
        },
        data_files = [],
        package_data = {},
        install_requires = [
            'PySimpleGUI==4.47.0',
            'boto3==1.18.36',
            'colorama==0.4.4',
            'pybuilder==0.12.10'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '',
        obsoletes = [],
    )
