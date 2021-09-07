from setuptools import setup
from os.path import join, dirname

setup(
    name='report_racing',
    version='1.1',
    packages=['report_racing'],
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type='text/markdown',
    author_email='dimapyatetsky@gmail.com'
    )
