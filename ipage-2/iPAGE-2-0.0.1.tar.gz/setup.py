import setuptools


with open("README.md", "r") as f:
    long_description = f.read()

REQUIRED_PACKAGES = ["pybiomart", "statsmodels", "scipy", "argparse", "numpy", "pandas",
                     "matplotlib", 'numba>=0.50.1']

setuptools.setup(
    name="iPAGE-2",
    version="0.0.1",
    install_requires=REQUIRED_PACKAGES,
    author="Artemy Bakulin, Matvei Khoroshkin, Hani Goodarzi",
    author_email="artemybakulin@gmail.com",
    description="A tool for the pathway analysis of differential gene expression",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/artemy-bakulin/ipage",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['bin/iPAGE2'],
)
