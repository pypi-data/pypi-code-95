# -*- coding: utf-8 -*-
"""
package/install module package ekca-service
"""

import sys
import os
from setuptools import setup

PYPI_NAME = 'ekca-plugin-privacyidea'

BASEDIR = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, os.path.join(BASEDIR, 'ekca_service', 'plugins', 'otp', 'privacyidea'))
import __about__

setup(
    name=PYPI_NAME,
    license=__about__.__license__,
    version=__about__.__version__,
    description='EKCA service OTP plugin for privacyIDEA',
    author=__about__.__author__,
    author_email=__about__.__mail__,
    maintainer=__about__.__author__,
    maintainer_email=__about__.__mail__,
    url='',
    download_url='',
    keywords=['PKI', 'SSH', 'SSH-CA', 'Certificate'],
    packages=['ekca_service.plugins.otp.privacyidea'],
    package_dir={'': '.'},
    test_suite='tests',
    python_requires='>=3.4.*',
    include_package_data=True,
    data_files=[],
    install_requires=[
        'setuptools',
        'ekca-service>=0.1.3',
        'requests>=2.22',
        'responses>=0.10'
    ],
    zip_safe=False,
    entry_points={
        'ekca_service.plugins.otp': [
            'privacyidea = ekca_service.plugins.otp.privacyidea:PrivacyIdeaOTPChecker',
        ],
    },
)
