import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
setup(
    name='shiprocket',
    version='1.0.1',
    packages=find_packages(),
    url='https://github.com/pupattan/shiprocket',
    license='MIT',
    include_package_data=True,
    keywords="python shiprocket ecommerce shipping",
    author='Pulak Pattanayak',
    long_description=README,
    long_description_content_type='text/markdown',
    author_email='pkbsdmp@gmail.com',
    description='Python APIs for shiprocket.in',
    classifiers =[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ]
)