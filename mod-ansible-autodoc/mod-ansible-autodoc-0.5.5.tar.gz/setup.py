from setuptools import setup, find_packages
from mod_ansible_autodoc import __version__

NAME = "mod-ansible-autodoc"
REPO = "mod-ansible-autodoc"

VERSION = __version__
ARCHIVE = f"v_{'_'.join(VERSION.split('.'))}.tar.gz"

setup(
    name=NAME,
    packages=find_packages(),
    version=VERSION,
    license="MIT",
    description="A wrapper for ansible-autodoc with formatted documentation",
    author="Renny Montero",
    author_email="rennym19@gmail.com",
    url=f"https://github.com/rennym19/{REPO}",
    download_url=f"https://github.com/rennym19/{REPO}/archive/{ARCHIVE}",
    keywords=["ANSIBLE", "AUTODOC", "MOD", "DOCUMENTATION", "FORK"],
    install_requires=[
        "ansible-autodoc-fork",
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [f"{NAME} = mod_ansible_autodoc.commands:run"]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
