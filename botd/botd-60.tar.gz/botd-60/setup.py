# This file is placed in the Public Domain.

from setuptools import setup

def read():
    return open("README.rst", "r").read()

setup(
    name="botd",
    version="60",
    url="https://github.com/bthate/botd",
    author="Bart Thate",
    author_email="bthate67@gmail.com",
    description="24/7 channel daemon",
    long_description=read(),
    license="Public Domain",
    zip_safe=True,
    install_requires=["botlib", "feedparser"],
    include_package_data=True,
    data_files=[
                ("etc/rc.d/", ["files/botd"]),
                ("share/doc/botd/", ["files/botd.8.md"]),
                ("lib/systemd/system", ["files/botd.service"]),
                ("man/man8", ["files/botctl.8.gz", "files/botd.8.gz"])
               ],
    scripts=["bin/botctl", "bin/botd"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: Public Domain",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
)
