from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.1.0'
DESCRIPTION = 'Encrypt'
LONG_DESCRIPTION = 'Quatno,m Encrypt'

# Setting up
setup(
    name="Encrypt_Lab",
    version=VERSION,
    author="Aviv Gili",
    author_email="aviv.orly@netvision.net.il",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy', 'PyQt5'],
    keywords=['python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3"
    ]
)