from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
  long_description = "\n" + f.read()

VERSION = '0.0.4'
DESCRIPTION = "Interacts with the Skyline Bots API"
LONG_DESCRIPTION = "A Python Package used to interact with the Skyline Bots API"

setup(
  name="skyline.py",
  version=VERSION,
  author="Yoshiboi18303 (Brice Coley)",
  author_email="<yoshiboi18303.t@gmail.com>",
  description=DESCRIPTION,
  long_description_content_type="text/markdown",
  long_description=long_description,
  packages=find_packages(),
  install_requires=["aiohttp>=3.7.4"],
  keywords=[
    'python',
    'skyline',
    'spyapi',
    'skyline api',
    'api',
    'skyline bots'
  ],
  classifiers=[
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Operating System :: Unix",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English"
  ]
)