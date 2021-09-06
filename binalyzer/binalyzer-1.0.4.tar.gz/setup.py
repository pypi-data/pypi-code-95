import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

__tag__ = "v1.0.4"
__build__ = 206
__version__ = "{}".format(__tag__)

setuptools.setup(
    name="binalyzer",
    version=__version__,
    author="Denis Vasilìk",
    author_email="contact@denisvasilik.com",
    url="https://binalyzer.denisvasilik.com",
    project_urls={
        "Bug Tracker": "https://github.com/denisvasilik/binalyzer/issues/",
        "Documentation": "https://binalyzer.readthedocs.io/en/latest/",
        "Source Code": "https://github.com/denisvasilik/binalyzer/",
    },
    description="Binary Data Analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Operating System :: POSIX :: Linux",
    ],
    dependency_links=[],
    package_dir={"binalyzer": "binalyzer"},
    package_data={},
    data_files=[("", ["CHANGELOG.md"])],
    setup_requires=[],
    install_requires=[
        "binalyzer-core==1.0.3",
        "binalyzer-cli==1.0.0",
        "binalyzer-data_provider==1.0.0",
        "binalyzer-template-provider==1.0.2",
        "binalyzer-rest==1.0.0",
        "binalyzer-wasm==1.0.0"
    ],
    entry_points={"console_scripts": ["binalyzer = binalyzer.cli:main"]},
)