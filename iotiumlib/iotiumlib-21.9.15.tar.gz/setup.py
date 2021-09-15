import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iotiumlib",
    version="21.09.15",
    author="Jawahar A",
    author_email="jawahar.a@iotium.io",
    description="ioTium API library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://iotium.io",
    packages=setuptools.find_packages(),
    license="Iotium | All rights reserved.",
    classifiers=(
        "Programming Language :: Python :: 3.5",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'requests',
        'urllib3'
    ]
)
