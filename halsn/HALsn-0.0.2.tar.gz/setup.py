from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.0.2'
DESCRIPTION = 'Host for SharkNinja BDP Python APIs'

# Setting up
setup(
    name="HALsn",
    version=VERSION,
    author="Mikhail Hyde",
    author_email="<hyde.mikhail@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['pandas', 'numpy', 'pyserial', 'awscli', 'boto3'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
    ]
)
