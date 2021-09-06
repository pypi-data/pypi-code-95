from setuptools import setup

version = "0.11"

long_description = "\n\n".join([open("README.rst").read(), open("CHANGES.rst").read()])

install_requires = []

tests_require = [
    "pytest",
    "mock",
    "pytest-cov",
    "pytest-flakes",
    "pytest-black",
]

setup(
    name="threedi-raster-edits",
    version=version,
    description="Threedi Raster Edits provides python tooling for threedi such as raster-conversion, alignment, fillers, checks and others",
    long_description=long_description,
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=["Programming Language :: Python", "Framework :: Django"],
    keywords=[],
    author="Chris Kerklaan",
    author_email="chris.kerklaan@nelen-schuurmans.nl",
    url="https://github.com/nens/threedi-raster-edits",
    license="MIT",
    packages=["threedi_raster_edits"],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={"test": tests_require},
    entry_points={
        "console_scripts": [
            "run-threedi-raster-edits = threedi_raster_edits.scripts:main"
        ]
    },
)
