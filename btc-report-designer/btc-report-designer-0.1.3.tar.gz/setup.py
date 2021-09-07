import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='btc-report-designer',
    version='0.1.3',
    packages=['report_designer'],
    include_package_data=True,
    license='BSD License',
    description='An application for creating reports based django models.',
    long_description=README,
    author='Pavel Boichenko',
    author_email='nuchimik@gmail.com',
    install_requires=[
        'Django>=2.2.11',
        'django-filter>=2.2.0',
        'django-mptt>=0.11.0',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
