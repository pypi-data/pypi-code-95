from setuptools import setup

setup(
    name='tkzs',
    version='0.0.4',
    author='Urchade Zaratiana',
    author_email='urchade.zaratiana@gmail.com',
    packages=['tkzs'],
    url='https://github.com/urchade/tkzs',
    license='LICENSE.txt',
    description='Some utils for tokenization in pytorch',
    long_description=open('README.md').read(),
    package_dir={'': 'src/'},
    long_description_content_type='text/markdown',
)