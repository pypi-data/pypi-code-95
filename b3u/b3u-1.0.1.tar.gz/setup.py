from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="b3u",
    version="1.0.1",
    packages=["b3u",],
    install_requires=[],
    license="MIT",
    url="https://github.com/nthparty/b3u",
    author="Andrei Lapets",
    author_email="a@lapets.io",
    description="Utility for extracting Boto3 configuration information "+\
                "and method parameters from AWS resource URIs.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    test_suite="nose.collector",
    tests_require=["nose"],
)
