from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="spatial-soul",
    version="0.1.2",
    description="Spatial -omics utilities library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/vibbits/spatial-soul',
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    packages=["spatialsoul"],
    install_requires=[],
)
