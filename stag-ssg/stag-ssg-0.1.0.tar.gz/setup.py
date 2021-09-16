from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f_:
    long_description = f_.read()


def main():
    setup(
        name="stag-ssg",
        description="Deadly simple static site generator",
        long_description=long_description,
        long_description_content_type="text/markdown",
        use_scm_version={"write_to": "src/stag/_version.py"},
        license="GPLv3+",
        author="Michał Góral",
        author_email="dev@goral.net.pl",
        url="https://git.goral.net.pl/mgoral/stag",
        platforms=["linux"],
        python_requires=">=3.7,<3.10",
        setup_requires=["setuptools_scm"],
        install_requires=[
            "attrs >=21, <22",
            "tomli >=1.2, <2.0",
            "jinja2 >=3 ,<4",
            "markdown >=3, <4",
            "python-dateutil >=2.8.0, <3",
            "python-slugify >=5, <6",
        ],
        extras_require={},
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "Environment :: Console",
            "Intended Audience :: End Users/Desktop",
            "Intended Audience :: Developers",
            "Intended Audience :: Information Technology",
            "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
            "Natural Language :: English",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Topic :: Internet :: WWW/HTTP :: Site Management",
            "Topic :: Utilities",
        ],
        packages=find_packages("src"),
        package_dir={"": "src"},
        entry_points={
            "console_scripts": [
                "stag=stag.stag:main",
            ],
        },
    )


if __name__ == "__main__":
    main()
