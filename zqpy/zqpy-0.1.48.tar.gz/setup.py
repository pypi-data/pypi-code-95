#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'zqpy'
DESCRIPTION = 'const tools manager'
URL = 'https://gitee.com/qingBB/zqpy'
EMAIL = '1620829248@qq.com'
AUTHOR = 'ZhouQing'
REQUIRES_PYTHON = '>=3.5.0'
# VERSION = '0.1.2'     # use in __version__.py
VERSION = False

# run zqpy module, require package
REQUIRED = [
    'requests', 'setuptools', 'qrcode', 'Pillow==8.1.2', 'natsort', 'moviepy', 'pretty_errors', 'datetime',
    'chardet', 'apscheduler', 'openpyxl', 'bs4',
    'opencv-python', 'aircv', 'pyautogui', 'appium-python-client', 'pytesseract', 'jieba','werkzeug'
]

# opertion require package
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
# VERSION 每次提交自动升级，所以不需要再手动改，除非是大版本提交
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """setup.py  upload"""

    description = 'create and publish package.'
    user_options = []

    @staticmethod
    def status(s):
        """print"""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('del before create')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('build source wheel(general) distribution')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('pass twine upload PyPI')
        os.system('twine upload dist/*')

        self.status('push to git')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')
        os.system('git add .')
        os.system('git stage')
        os.system('git commit -m "{0}{1}"'.format(about['__version__'], input('请输入提交日志信息-> ')))
        os.system('git push')

        # 自动升级下一个小版本
        import zqpy
        versionPath = os.path.join(here, project_slug, '__version__.py')
        strValue = zqpy.FileService.ReadFile(versionPath)
        versionList = about['__version__'].split('.')
        strValue = strValue.replace(versionList[2],str(int(versionList[2])+1))
        zqpy.FileService.WriteFile(versionPath, strValue)
        print('自动版本号+1  完成\n\n')

        import zqpy
        for item in sys.path:
            if item.endswith("\\lib\\site-packages"):
                zqpy.FileService.CopyDirs("./build/lib", item)
                print('./build/lib -> 复制到 %s\n\n'%item)
                
        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    zip_safe=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)