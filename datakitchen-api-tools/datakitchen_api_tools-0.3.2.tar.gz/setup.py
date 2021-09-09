import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datakitchen_api_tools",
    version="0.3.2",
    author="Armand Halbert",
    author_email="armand@datakitchen.io",
    description="Python libray for working with DataKitchen's API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    test_suite='nose.collector',
    tests_require=['nose'],
    packages=setuptools.find_packages(),
    install_requires=['requests'],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Operating System :: OS Independent",
    ],
)
