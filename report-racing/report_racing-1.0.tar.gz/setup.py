from setuptools import setup
from os.path import join, dirname

setup(
    name='report_racing',
    version='1.0',
    packages=['script_for_create_standings'],
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type='text/markdown',
    author_email='dimapyatetsky@gmail.com'
    )
