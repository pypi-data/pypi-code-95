import re

import setuptools


def read_file(path):
    with open(path, "r") as handle:
        return handle.read()


def read_version():
    try:
        s = read_file("VERSION")
        m = re.match(r"v(\d+\.\d+\.\d+(-.*)?)", s)
        return m.group(1)
    except FileNotFoundError:
        return "0.0.0"


long_description = read_file("docs/source/description.rst")
version = read_version()

setuptools.setup(
    name="apparatus",
    description="""""",
    keywords="",
    long_description=long_description,
    include_package_data=True,
    version=version,
    url="https://gitlab.com/greenhousegroup/ai/libraries/apparatus/",
    author="Greenhouse AI team",
    author_email="ai@greenhousegroup.com",
    package_dir={"apparatus": "src/apparatus"},
    entry_points={"console_scripts": ["apparatus = apparatus.__main__:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "miniscule>=0.4.0,<2",
        "clicasso>=0.4.0",
        "retry>0.9,<2",
        "tabulate>=0.8.9",
        "pydantic==1.*",
    ],
    data_files=[(".", ["VERSION"])],
    setup_requires=["pytest-runner"],
    tests_require=["pytest>=4"],
    packages=setuptools.find_packages("src"),
)
