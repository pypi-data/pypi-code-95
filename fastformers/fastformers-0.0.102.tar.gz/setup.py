import setuptools
import os
import re

package_name = "fastformers"
package_dir = "src"


def parse_version() -> str:
    with open(os.path.join(package_dir, package_name, "_version.py"), "rt") as fh:
        version_contents = fh.read()
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_contents, re.M)
    if match:
        return match.group(1)
    else:
        raise RuntimeError("Unable to find version string")


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=package_name,
    version=parse_version(),
    author="datarootlabs",
    author_email="dev@datarootlabs.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    package_dir={"": package_dir},
    packages=setuptools.find_packages(where=package_dir),
    python_requires=">=3.6",
    install_requires=[
        'torch>=1.6',
    ]
)
