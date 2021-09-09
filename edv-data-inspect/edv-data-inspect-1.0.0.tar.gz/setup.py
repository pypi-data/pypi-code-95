from setuptools import setup

def readme():
    with open("README.md") as f:
        README = f.read()
    return README

setup(
    name="edv-data-inspect",
    version="1.0.0",
    description="A Python package that helps you to inspect the edv data",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/iamdarshan7/EdvRegex",
    author="Darshan Thapa",
    author_email="darshanthapa872@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["edv_data_inspect"],
    include_package_data=True,
    install_requires=["pyperclip==1.8.0", "re"],
    entry_points={
        "console_scripts": [
            "edv-data-inspect=edv_data_inspect.edvRegex:main",
        ]
    },
)
