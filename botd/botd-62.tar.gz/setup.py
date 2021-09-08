# This file is placed in the Public Domain.

from setuptools import setup

def read():
    return open("README.rst", "r").read()

setup(
    name="botd",
    version="62",
    url="https://github.com/bthate/botd",
    author="Bart Thate",
    author_email="bthate67@gmail.com",
    description="24/7 channel daemon",
    long_description=read(),
    license="Public Domain",
    packages=["bot"],
    include_package_data=True,
    data_files=[('share/doc/botd', [
                                    'docs/botdgreenline.png',
                                    'docs/botdgreenline2.png',
                                    'docs/botdgreensmile.png',
                                    'docs/botdgreen.png',
                                    'docs/conf.py',
                                    'docs/index.rst',
                                    'docs/aasource.rst',
                                    'docs/_templates/base.rst',
                                    'docs/_templates/class.rst',
                                    'docs/_templates/layout.html',
                                    'docs/_templates/module.rst',
                                    'files/bot.1.md',
                                    'files/botd.8.md'
                                   ]),
                ("etc/rc.d/", ["files/botd"]),
                ("share/doc/botd/", ["files/botd.8.md"]),
                ("lib/systemd/system", ["files/botd.service"]),
                ("man/man1", ["files/bot.1.gz"]),
                ("man/man8", ["files/botctl.8.gz", "files/botd.8.gz"])],
    scripts=["bin/bot", "bin/botctl", "bin/botd"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: Public Domain",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ]
)
