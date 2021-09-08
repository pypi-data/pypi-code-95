from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="bitlist",
    version="0.4.0",
    packages=["bitlist",],
    install_requires=["parts~=1.0.3",],
    license="MIT",
    url="https://github.com/lapets/bitlist",
    author="Andrei Lapets",
    author_email="a@lapets.io",
    description="Minimal Python library for working "+\
                "with bit vectors natively.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    test_suite="nose.collector",
    tests_require=["nose"],
)
