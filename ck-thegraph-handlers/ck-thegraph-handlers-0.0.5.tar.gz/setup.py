import re
from pathlib import Path
from typing import List

from setuptools import find_packages, setup


def get_version(package: str) -> str:
    """
    Extract package version, located in the `src/package/__version__.py`.
    """
    version = Path("src", package, "__version__.py").read_text()
    pattern = r"__version__ = ['\"]([^'\"]+)['\"]"
    return re.match(pattern, version).group(1)  # type: ignore


def get_requirements(req_file: str) -> List[str]:
    """
    Extract requirements from provided file.
    """
    req_path = Path(req_file)
    requirements = req_path.read_text().split("\n") if req_path.exists() else []
    return requirements


def get_long_description(readme_file: str) -> str:
    """
    Extract README from provided file.
    """
    readme_path = Path(readme_file)
    long_description = (
        readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    )
    return long_description


setup(
    name="ck-thegraph-handlers",
    version=get_version("thegraph_handlers"),
    description="Integrations of Ethereum services through https://thegraph.com",
    long_description=get_long_description("README.md"),
    long_description_content_type="text/markdown",
    author="crypkit",
    author_email="info@crypkit.com",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=get_requirements("requirements.txt"),
    extras_require={
        "dev": get_requirements("dev-requirements.txt"),
        "test": get_requirements("test-requirements.txt"),
        "all": get_requirements("dev-requirements.txt")
        + get_requirements("test-requirements.txt"),
    },
)
