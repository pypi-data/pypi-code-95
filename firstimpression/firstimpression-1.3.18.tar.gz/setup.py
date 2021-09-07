from setuptools import find_packages, setup
from os import path

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md')) as f:
    README = f.read()

setup(
    name='firstimpression',
    packages=find_packages(),
    version='1.3.18',
    description='First Python library',
    long_description=README,
    long_description_content_type='text/markdown',
    author='FirstImpression',
    author_email='programming@firstimpression.nl',
    license='MIT',
    install_requires=["requests", "geopy", "wheel", "lxml", "pytz", "socketIO_client", "requests[security]", "w3lib", "unidecode", "numpy"],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 2.7'
    ],
)
