# Copyright 2013-2014 MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from setuptools import setup

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 3
Topic :: Database
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Unix
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
"""
setup(
    name="mongo-connector-transaction",
    use_scm_version=True,
    author="MongoDB, Inc.",
    author_email="amradelkhalil@gmail.com",
    description="Mongo Connector Transaction Support",
    keywords=["mongo-connector-transaction", "mongo", "mongodb", "solr", "elasticsearch", "transaction"],
    url="https://github.com/AmrAdelKhalil/mongo-connector",
    platforms=["any"],
    classifiers=classifiers.split("\n"),
    install_requires=[
        "pymongo >= 2.9",
        "importlib_metadata>=0.6",
        "autocommand",
        "importlib_resources",
    ],
    packages=["mongo_connector", "mongo_connector.doc_managers"],
    package_data={"mongo_connector.doc_managers": ["schema.xml"]},
    entry_points={
        "console_scripts": ["mongo-connector = mongo_connector.connector:main"]
    },
    extras_require={
        "elastic5": ["elastic2-doc-manager-transaction[elastic5]"]
    },
    setup_requires=[
        "setuptools_scm>=1.5",
    ],
    python_requires=">=3.4",
)
