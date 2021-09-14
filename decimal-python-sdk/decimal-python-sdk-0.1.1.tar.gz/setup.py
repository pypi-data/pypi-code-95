import setuptools

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="decimal-python-sdk",
    version="0.1.1",
    author="DecimalTeam",
    description="",
    long_description=long_description,
    install_requires=required,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/decimalteam/decimal-python-sdk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
