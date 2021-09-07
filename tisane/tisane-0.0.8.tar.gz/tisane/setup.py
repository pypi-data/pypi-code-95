import setuptools

with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tisane",
    version="0.0.1",
    author="Eunice Jun",
    author_email="emjun@cs.washington.edu",
    description="Tisane: Authoring Statistical Models via Formal Reasoning from Conceptual and Data Relationships",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emjun/tisane",
    packages=setuptools.find_packages(),
    install_requires=[
        "pandas",
        "networkx",
        "z3-solver",
        "statsmodels",
        "more-itertools",
        "pydot",
        "tweedie",
        "Flask",
        "plotly",
        "dash",
        "dash-bootstrap-components",
        "dash-daq",
        "patsy",
        "coverage",
        "pytest-cov",
        "pytest",
        "black",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    # python_requires='3.7.11',
)
