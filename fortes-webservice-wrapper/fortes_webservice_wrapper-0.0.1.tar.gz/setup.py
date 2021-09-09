from setuptools import setup

import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

# Setting up
setup(
    name="fortes_webservice_wrapper",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Imobanco",
    description="Webservice de comunicação com o Fortes Financeiro",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/imobanco/fortes-webservice-wrapper/",
    packages=[
        "fortes_webservice_wrapper",
        "fortes_webservice_wrapper.wrapper",
        "fortes_webservice_wrapper.models",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: Portuguese (Brazilian)",
        "Operating System :: OS Independent",
        "Topic :: Documentation :: Sphinx",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        "Topic :: Utilities",
        "",
        "",
    ],
    python_requires=">=3.8",
    install_requires=["python-decouple>=3.3", "pydantic>=1.7.0", "zeep>=4.0.*"],
)
