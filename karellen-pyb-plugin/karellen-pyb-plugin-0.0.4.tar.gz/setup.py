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
        name = 'karellen-pyb-plugin',
        version = '0.0.4',
        description = 'Karellen PyBuilder Plugin',
        long_description = '# Karellen PyBuilder Plugin\n\n[Karellen](https://www.karellen.co/karellen/) [PyBuilder](https://pybuilder.io/) Plugin\n\n[![Gitter chat](https://badges.gitter.im/karellen/gitter.svg)](https://gitter.im/karellen/lobby)\n\nThis is the main PyBuilder plugin for all of the projects under [Karellen](https://www.karellen.co/) umbrella.\nThis plugin governs the following PyBuilder project settings:\n\n1. Code style and copyright headers.\n2. Coverage passing threshold.\n3. Documentation building and style.\n4. Code packaging, packaging metadata and signing.\n\nIn order to make sure your project conforms to Karellen standards, use this plugin by adding the following to your `build.py`:\n\n```python\n\nfrom pybuilder.core import use_plugin\n\n# ... #\n\nuse_plugin("pypi:karellen_pyb_plugin", ">=0.0.1")\n\n```\n\n## For Developers\n\n[Karellen PyBuilder Plugin Issue Tracker](https://github.com/karellen/karellen-pyb-plugin/issues)\n\n[Karellen PyBuilder Plugin Source Code](https://github.com/karellen/karellen-pyb-plugin)\n',
        long_description_content_type = 'text/markdown',
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python'
        ],
        keywords = '',

        author = 'Karellen, Inc',
        author_email = 'supervisor@karellen.co',
        maintainer = 'Arcadiy Ivanov',
        maintainer_email = 'arcadiy@karellen.co',

        license = 'Apache License, Version 2.0',

        url = 'https://github.com/karellen/karellen-pyb-plugin',
        project_urls = {
            'Bug Tracker': 'https://github.com/karellen/karellen-pyb-plugin/issues',
            'Documentation': 'https://github.com/karellen/karellen-pyb-plugin/',
            'Source Code': 'https://github.com/karellen/karellen-pyb-plugin/'
        },

        scripts = [],
        packages = ['karellen_pyb_plugin'],
        namespace_packages = [],
        py_modules = [],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '',
        obsoletes = [],
    )
