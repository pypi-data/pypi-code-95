import pathlib
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="salesdredge",
    version="1.0.3",
    description="This is the API for the Salesdredge.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="http://www.salesdredge.com",
    author="Christopher Roos",
    author_email="roos.christopher@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "beautifulsoup4==4.9.3",
        "boto3==1.18.18",
        "botocore==1.21.18",
        "bs4==0.0.1",
        "certifi==2021.5.30",
        "charset-normalizer==2.0.4",
        "elasticsearch==7.13.1",
        "filelock==3.0.12",
        "idna==3.2",
        "jmespath==0.10.0",
        "numpy==1.21.1",
        "pandas==1.3.1",
        "phonenumbers==8.12.29",
        "python-dateutil==2.8.2",
        "pytz==2021.1",
        "requests==2.26.0",
        "requests-file==1.5.1",
        "s3transfer==0.5.0",
        "six==1.16.0",
        "soupsieve==2.2.1",
        "tldextract==3.1.0",
        "urllib3==1.26.6",
    ],
    entry_points={
        "console_scripts": [
            "salesdredge=salesdredge.__main__:main",
        ]
    },
)