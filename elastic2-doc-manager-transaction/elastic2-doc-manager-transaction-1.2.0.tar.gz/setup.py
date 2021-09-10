import setuptools

setuptools.setup(
    name="elastic2-doc-manager-transaction",
    use_scm_version=True,
    maintainer="mongodb",
    description="es2 for mongo-connector",
    platforms=["any"],
    author="Amr Adel",
    author_email="amradelkhalil@gmail.com",
    url="https://github.com/AmrAdelKhalil/elastic2-doc-manager",
    install_requires=["mongo-connector-transaction", "importlib_metadata"],
    python_requires=">=3.4",
    extras_require={
        "aws": ["boto3 >= 1.4.0", "requests-aws-sign >= 0.1.2"],
        "elastic2": ["elasticsearch>=2.0.0,<3.0.0"],
        "elastic5": ["elasticsearch>=5.0.0,<6.0.0"],
    },
    packages=["mongo_connector", "mongo_connector.doc_managers"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
    ],
    keywords=["mongo-connector-transaction", "mongodb", "elastic", "elasticsearch", "transaction"],
    setup_requires=["setuptools_scm>=1.15"]
)
