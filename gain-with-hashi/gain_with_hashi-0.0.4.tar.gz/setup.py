from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.4'
DESCRIPTION = 'Gain Followers On Instagram'
LONG_DESCRIPTION = 'Gain Followers On Instagram with @gain_with_hashi'

setup(
    name="gain_with_hashi",
    version=VERSION,
    author="kooriez",
    author_email="<hashid0003@gmail.com.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['instabot',],
    keywords=['python', 'instabot', 'ig_bot', 'insta py', 'instagram', 'auto followers'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
