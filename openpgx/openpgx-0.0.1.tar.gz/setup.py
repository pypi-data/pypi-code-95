#! /usr/bin/env python

DESCRIPTION = "openpgx: PGx tool for converting star alleles of pharmacogenes to gene-drug recommendations"
LONG_DESCRIPTION = """\
OpenPGx is software to convert human's genotype to phenotype and annotate with gene-drug recommendations (for all drugs having recommendations in CPIC, DPWG, or FDA pharmacogenomics databases).
"""

DISTNAME = 'openpgx'
MAINTAINER = 'Monika Krzyżanowska'
MAINTAINER_EMAIL = 'monigenomi@gmail.com'
URL = 'https://openpgx.com/'
LICENSE = 'GPLv3'
DOWNLOAD_URL = 'https://github.com/monigenomi/openpgx/'
VERSION = '1.0.0'
PYTHON_REQUIRES = ">=3.9"

INSTALL_REQUIRES = [
    
]

EXTRAS_REQUIRE = {
    'dev': [
    ]
}


PACKAGES = [
    'openpgx',
]

CLASSIFIERS = [
    'Intended Audience :: Science/Research',
    'Programming Language :: Python :: 3.9',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
]


if __name__ == "__main__":

    from setuptools import setup

    import sys
    if sys.version_info[:2] < (3, 6):
        raise RuntimeError("openpgx requires python >= 3.6.")

    setup(
        name=DISTNAME,
        author=MAINTAINER,
        author_email=MAINTAINER_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license=LICENSE,
        url=URL,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        python_requires=PYTHON_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        packages=PACKAGES,
        classifiers=CLASSIFIERS
    )

