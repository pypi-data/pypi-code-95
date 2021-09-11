# -*- coding: utf-8 -*-
# ClickNLoad2FeedCrawler
# Projekt von https://github.com/rix1337

import setuptools

try:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()
except:
    import io

    long_description = io.open('README.md', encoding='utf-8').read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="cnl2feedcrawler",
    version="1.1.1",
    author="rix1337",
    author_email="",
    description="Intercept, decrypt and forward CnL to FeedCrawler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rix1337/ClickNLoad2FeedCrawler",
    packages=["cnl2feedcrawler"],
    include_package_data=True,
    install_requires=required,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    entry_points={
        'console_scripts': [
            'cnl2feedcrawler = cnl2feedcrawler.cnl2feedcrawler:main',
        ],
    },
)
