import setuptools
# from pathlib import Path
# from os import getenv

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='migrations-ml',
    version='0.0.11',
    author='Jacques Nel',
    author_email='jacques.nel@migrations.ml',
    description='Migrations.ML advanced bond risk analytics data REST API wrapper.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://migrations.ml',
    install_requires=[
        'pandas>=1.3.2',
        'requests>=2.26.0',
        'numpy>=1.21.2'
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: Other/Proprietary License',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Financial and Insurance Industry',
        'Natural Language :: English',
        'Topic :: Office/Business :: Financial'
    ],
    python_requires='>=3.8',
    test_suite='tests'
)
