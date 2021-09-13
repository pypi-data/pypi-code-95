from setuptools import setup, find_packages

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='PRPConnector',
    packages=find_packages(),
    version=1.1,
    license='MIT',
    description='Connector for Clients to the PRP-Backend',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Manuel Bieri',
    author_email='marbl.ch@outlook.com',
    url='https://github.com/manuelbieri/PRP-APIConnect',
    download_url='https://github.com/manuelbieri/PRP-APIConnect/archive/refs/tags/v1.0.tar.gz',
    keywords=['API'],
    classifiers=[
        'Development Status :: 4 - Beta',  # "3 - Alpha" / "4 - Beta" / "5 - Production/Stable"
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
