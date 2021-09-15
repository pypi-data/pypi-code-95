# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['robocorp_dialog']

package_data = \
{'': ['*'],
 'robocorp_dialog': ['Dialog.app/Contents/*',
                     'Dialog.app/Contents/MacOS/*',
                     'Dialog.app/Contents/MacOS/AppKit/*',
                     'Dialog.app/Contents/MacOS/CoreFoundation/*',
                     'Dialog.app/Contents/MacOS/Foundation/*',
                     'Dialog.app/Contents/MacOS/WebKit/*',
                     'Dialog.app/Contents/MacOS/lib-dynload/*',
                     'Dialog.app/Contents/MacOS/objc/*',
                     'Dialog.app/Contents/MacOS/robocorp_dialog/static/*',
                     'Dialog.app/Contents/Resources/*',
                     'Dialog.app/Contents/Resources/robocorp_dialog/static/*',
                     'Dialog.app/Contents/_CodeSignature/*',
                     'Dialog/*',
                     'Dialog/robocorp_dialog/static/*',
                     'Dialog/webview/lib/*',
                     'Dialog/webview/lib/x64/*',
                     'Dialog/webview/lib/x86/*',
                     'static/*']}

extras_require = \
{':sys_platform == "linux"': ['pywebview>=3.5,<4.0',
                              'PyQt5>=5.15.2,<6.0.0',
                              'PyQtWebEngine>=5.15.2,<6.0.0']}

entry_points = \
{'console_scripts': ['robocorp-dialog = robocorp_dialog.main:main']}

setup_kwargs = {
    'name': 'robocorp-dialog',
    'version': '0.4.0',
    'description': 'Dialog for querying user input',
    'long_description': '# Robocorp Dialog\n\nA separate executable which opens a dialog window for querying user input.\nContent created dynamically based on JSON spec.\n\nUsed in [Dialogs](https://github.com/robocorp/rpaframework/tree/master/packages/dialogs) library.\n',
    'author': 'Ossi Rajuvaara',
    'author_email': 'ossi@robocorp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://rpaframework.org/',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
