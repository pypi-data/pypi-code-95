import codecs
import os
import re


from setuptools import setup

dirname = os.path.abspath(os.path.dirname(__file__))

with codecs.open(
    os.path.join(dirname, "d1ct", "__init__.py"),
    mode="r",
    encoding="utf-8",
) as fp:
    try:
        content = fp.read()
        version = re.findall(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)[0]
        description = re.findall(
            r"^__description__ = ['\"]([^'\"]*)['\"]", content, re.M
        )[0]
    except Exception:
        raise RuntimeError("unable to determine version")

setup(
    name="d1ct",
    version=version,
    url="https://github.com/ultrafunkamsterdam/d1ct",
    license="MIT",
    author="UltrafunkAmsterdam",
    author_email="",
    description=description,
    packages=["d1ct"],
)
