# aws_creds_replace
from setuptools import find_packages
from setuptools import setup
from pip._internal.req import parse_requirements


# Pulls pip packages with versions from the requirements file
install_requires = parse_requirements("requirements.txt", session="rollcred")
try:
    requirements = [str(ir.req) for ir in install_requires]
except:
    requirements = [str(ir.requirement) for ir in install_requires]

setup(
    name="rollcred",
    version="0.0.4",
    author="Traey Hatch",
    author_email="thatch@newmathdata.com",
    url="https://github.com/New-Math-Data/rollcred.git",
    description="",
    long_description="AWS Creds Replace Library",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    setup_requires=[],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={"console_scripts": ["rollcred=rollcred.main:cli"]},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    dependency_links=[],
    include_package_data=False,
)
