import setuptools, os

with open("README.md", "r") as fh:
    long_description = fh.read()

# Get the version from the glia module without importing it.
with open(os.path.join(os.path.dirname(__file__), "dbbs_catalogue", "__init__.py"), "r") as f:
    for line in f:
        if "__version__ = " in line:
            exec(line)
            break


setuptools.setup(
    name="dbbs-catalogue",
    version=__version__,
    author="Robin De Schepper",
    author_email="robingilbert.deschepper@unipv.it",
    description="DBBS catalogue of Arbor dialect NMODL files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dbbs-lab/catalogue",
    license="GPLv3",
    packages=["dbbs_catalogue"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    package_data=dict(dbbs_catalogue=["mod/*"]),
    entry_points={"glia.catalogue": ["dbbs = dbbs_catalogue:catalogue"]},
    install_requires=["nrn-glia>=0.4"],
)
