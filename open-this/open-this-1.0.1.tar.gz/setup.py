from setuptools import setup

def readme():
    with open("README.md") as f:
        README = f.read()
    return README

setup(
    name="open-this",
    version="1.0.1",
    description="A Python tiny package that opens Facebook, Youtube from terminal",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/iamdarshan7/OpenSocialMediaWithCLI",
    author="Darshan Thapa",
    author_email="darshanthapa872@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["open_this"],
    include_package_data=True,
    install_requires=["pyperclip==1.8.0"],
    entry_points={
        "console_scripts": [
            "open-this=open_this.socialMedia:main",
        ]
    },
)
