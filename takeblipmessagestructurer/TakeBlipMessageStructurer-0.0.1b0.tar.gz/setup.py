import setuptools

with open("README_PACKAGE.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="TakeBlipMessageStructurer",
    version="0.0.1b",
    author="Data and Analytics Research",
    author_email="analytics.dar@take.net",
    credits=['Renan Santos'],
	keywords='messagestructurer',
    description="Message Structurer Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
	install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	include_package_data = True
)