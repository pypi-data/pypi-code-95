# -*- coding: utf-8 -*-
# Copyright (C) 2009-2020 Martin Slouf <martinslouf@users.sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from setuptools import setup, find_packages

VERSION = "0.7.8.1"
DESCRIPTION = """Summer -- light weight Python 3 application framework"""
LONG_DESCRIPTION = """Summer is light weight Python 3 application framework to support generic
application development.  It provides support for business object
management, ORM (mapping, declarative transactions), LDAP and localization.
Inspired by famous Java Spring application framework."""

CLASSIFIERS = """
Programming Language :: Python :: 3 :: Only
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Operating System :: OS Independent
Development Status :: 4 - Beta
Intended Audience :: Developers
Topic :: Software Development :: Libraries :: Application Frameworks
"""

setup(
    name="summer",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="Martin Šlouf",
    author_email="martinslouf@sourceforge.net",
    url="http://py-summer.sourceforge.net/",
    license="Lesser General Public Licence version 3",
    classifiers=[i for i in CLASSIFIERS.split("\n") if i],
    keywords="framework development",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7, <4",
    extras_require={
        "sqlalchemy":  ["sqlalchemy == 1.3.23"],
        "ldap": ["ldap3 == 2.9"],
    },
    package_data={
        "summer": ["sample/*.sample"],
    },
)
