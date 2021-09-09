import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="G4S",  # Replace with your own username
    version="0.1.2",
    author="PTST",
    author_email="patrick@steffensen.io",
    description="API interface for G4S Alarms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PTST/G4S_Alarm_Py",
    packages=setuptools.find_packages(),
    install_requires=["requests >= 2.23.0", "python-dateutil >= 2.8.1"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
