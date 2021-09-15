import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
setup(
    name='django-oscar-razorpay',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/pupattan/django-oscar-razorpay',
    license='MIT',
    include_package_data=True,
    keywords="django django-oscar razorpay payment",
    author='Pulak Pattanayak',
    long_description=README,
    long_description_content_type='text/markdown',
    author_email='pkbsdmp@gmail.com',
    description='Django oscar app for Razorpay',
    classifiers =[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ]
)