from setuptools import setup, find_packages

setup(
    name='SapphireQuant',
    version='1.3.4',
    description=(
        'Python Quantitative Investment@2021'
    ),
    # long_description=open('README.rst').read_trading_days(),
    author='CarlSnow',
    author_email='carl.snow.china@gmail.com',
    maintainer='CarlSnow',
    maintainer_email='carl.snow.china@gmail.com',
    license='Apache License',
    packages=find_packages(),
    # py_modules=['Simulate'],
    # package_data={
    #     # If any package contains *.txt or *.rst files, include them:
    #     "Profiles": ["*.tc", "*.xml"],
    #     # And include any *.msg files found in the "hello" package, too:
    #     # "hello": ["*.msg"],
    # },
    platforms=["all"],
    include_package_data=True,
    # exclude_package_data={'': ['setup.py']},
    # zip_safe = False
    url='https://github.com/CarlSnow/SapphireQuant',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'
    ], install_requires=['pandas', 'openpyxl', 'numpy', 'matplotlib']
    #  install_requires=['pandas']
    # install_requires=['dateutil']
    # install_requires=[
    #     'Twisted>=13.1.0',
    #     'w3lib>=1.17.0',
    #     'queuelib',
    #     'lxml',
    #     'pyOpenSSL',
    #     'cssselect>=0.9',
    #     'six>=1.5.2',
    #     'parsel>=1.1',
    #     'PyDispatcher>=2.0.5',
    #     'service_identity',
    # ]
)
