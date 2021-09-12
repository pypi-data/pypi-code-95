from setuptools import setup
import setuptools
setup(
    name='oapi-parser',
    version='1.0.0A',
    # packages=['oapi_parse'],
    # package_dir = {'oapi_parse': 'oapi_parse/commons'},
    packages=setuptools.find_packages(exclude=("tests",)),
    url='',
    license='',
    python_requires='>3.6',
    include_package_data=True,
    author='Srikanth_Srigakolapu',
    author_email='srikanth.srigakolapu@gmail.com',
    description='A simple Open API parser',
    long_description = 'The OAPI_Parser is a simple and lightweight library to process your open api documents. Currently supporting both Json and Xml formats.',
    install_requires= ["pyyaml","jsonschema","pytest"]
)
