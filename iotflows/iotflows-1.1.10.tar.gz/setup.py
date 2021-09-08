import pathlib2
from setuptools import setup, find_packages

HERE = pathlib2.Path(__file__).parent

VERSION = '1.1.10'
PACKAGE_NAME = 'iotflows'
AUTHOR = 'IoTFLows Inc'
AUTHOR_EMAIL = 'info@iotflows.com'
URL = 'https://github.com/iotflows/iotflows-python'

LICENSE = 'Apache License 2.0'
DESCRIPTION = 'IoTFlows Open Source Python WebSocket SDK.'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'pathlib2',
      'setuptools',
      'paho-mqtt', 
      'requests'      
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages()
      )