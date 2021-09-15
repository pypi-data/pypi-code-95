import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

INSTALL_REQUIRES = [
    "requests",
    "python-dotenv",
    ]

TEST_REQUIRES = [
    ]

EXAMPLE_REQUIRES = [
    ]

setuptools.setup(
        name='endaq-cloud',
        version='1.0.0b1',
        author='Mide Technology',
        author_email='help@mide.com',
        description='The cloud subpackage for endaq-python',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/MideTechnology/endaq-python-cloud',
        license='MIT',
        classifiers=['Development Status :: 4 - Beta',
                     'License :: OSI Approved :: MIT License',
                     'Natural Language :: English',
                     'Programming Language :: Python :: 3.5',
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',
                     'Programming Language :: Python :: 3.9',
                     'Topic :: Scientific/Engineering',
                     ],
        keywords='ebml binary ide mide endaq',
        packages=['endaq.cloud'],
        package_dir={'endaq.cloud': './endaq/cloud'},
        install_requires=INSTALL_REQUIRES,
        extras_require={
            'test': INSTALL_REQUIRES + TEST_REQUIRES,
            'example': INSTALL_REQUIRES + EXAMPLE_REQUIRES,
            },
        entry_points=dict(
            console_scripts=[
                "endaq-cloud=endaq.cloud.API_wrapper:main",
            ],
        ),
)
