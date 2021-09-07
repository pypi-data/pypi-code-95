from setuptools import find_packages, setup

setup(
    name="trulie",
    author="Stanislav Schmidt",
    use_scm_version={
        "write_to": "src/trulie/version.py",
        "write_to_template": '"""The package version."""\n__version__ = "{version}"\n',
        "local_scheme": "no-local-version",
    },
    url="https://github.com/Stannislav/trulie",
    package_dir={"": "src"},
    packages=find_packages("src"),
    extras_require={
        "dev": [
            "black",
            "flake8",
            "isort",
            "pydocstyle",
            "pytest",
            "pytest-cov",
            "tox",
        ]
    },
)
