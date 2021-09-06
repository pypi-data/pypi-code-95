from setuptools import setup

setup(
    name='byte_search',
    version='0.5.6',
    author='Urchade Zaratiana',
    author_email='urchade.zaratiana@gmail.com',
    packages=['byte_search'],
    url='https://github.com/urchade/byte_search',
    license='LICENSE.txt',
    description='Fast lexical search',
    long_description=open('README.md').read(),
    package_dir={'': 'src/'},
    long_description_content_type='text/markdown',
)