#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()
    """
    GitHub does not align rst images correctly and PyPI does not accept raw html, so the html code stays in the git repo
    and gets replaced with the rst equivalent here to show correctly in PyPI
    """
    gif_html_code = """.. raw:: html

    <embed>
        <p align="center">
            <img src="https://github.com/douglascdev/aoba_discord_bot/raw/main/aoba.gif" alt="Aoba"/>
        </p>
    </embed>"""
    gif_rst_code = """
.. image:: https://github.com/douglascdev/aoba_discord_bot/raw/main/aoba.gif
    :align: center
"""
    readme = readme.replace(gif_html_code, gif_rst_code)

    png_html_code = """.. raw:: html

    <embed>
        <p align="center">
            <img src="https://github.com/douglascdev/aoba_discord_bot/raw/main/aoba.png" alt="Aoba"/>
        </p>
    </embed>"""
    png_rst_code = """
.. image:: https://github.com/douglascdev/aoba_discord_bot/raw/main/aoba.png
    :align: center
"""
    readme = readme.replace(png_html_code, png_rst_code)

with open("HISTORY.rst") as history_file:
    history = history_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read()

test_requirements = [
    "pytest>=3",
]

setup(
    author="Douglas Carvalho",
    author_email="douglasc.dev@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="Aoba, the cutest Python Discord bot in all of GitHub.",
    entry_points={
        "console_scripts": [
            "aoba_discord_bot=aoba_discord_bot.cli:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="aoba_discord_bot",
    name="aoba_discord_bot",
    packages=find_packages(include=["aoba_discord_bot", "aoba_discord_bot.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/douglascdev/aoba_discord_bot",
    version="0.1.12",
    zip_safe=False,
)
