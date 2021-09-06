from setuptools import setup, find_packages


setup(
    name='l10n_uy_api',
    version='1.3.3',
    description='Libreria para localizacion Uruguaya',
    long_description='Libreria para localizacion Uruguaya',
    url='',
    author='BLUEORANGE GROUP',
    author_email='daniel@blueorange.com.ar',
    license='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='Libreria para localizacion Uruguaya',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'zeep==2.5.0',
        'python-dateutil',
        'M2Crypto',
        'pytz',
        'unidecode',
        'bs4'
    ],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={},
    include_package_data=True
)
