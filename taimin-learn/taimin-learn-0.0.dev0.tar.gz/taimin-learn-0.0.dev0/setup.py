import tmlearn
import tmlearn._min_dependencies as min_deps

DISTNAME = "taimin-learn"
DESCRIPTION = "A set of useless modules for machine learning"
with open("README.md") as f:
    LONG_DESCRIPTION = f.read()
MAINTAINER = "Taimin Zhang"
MAINTAINER_EMAIL = "zhangtaimin1992@gmail.com"
LICENSE = "MIT"

VERSION = tmlearn.__version__


def setup_package():
    metadata = dict(
        name=DISTNAME,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        license=LICENSE,
        version=VERSION,
        long_description=LONG_DESCRIPTION,
        python_requires=">=3.7",
        install_requires=min_deps.tag_to_packages["install"],
    )
    from setuptools import setup
    setup(**metadata)


if __name__ == "__main__":
    setup_package()
