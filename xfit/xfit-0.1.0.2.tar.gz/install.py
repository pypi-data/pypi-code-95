from setuptools import setup, find_packages
from version import VERSION

with open("README.md") as readme_file:
        README = readme_file.read()

setup(include_package_data=True)

setup_args = dict(
        name="xfit",
        version=VERSION,
        description="Package for fitting XRF spectra. Based on xraylib",
        long_description_content_type="text/markdown",
        long_description = README,
        license='MIT',
        packages = ["xfit"],
        author = "Sergio A. B. Lins",
        author_email = "sergio.lins@roma3.infn.it",
        url = "https://github.com/linssab/xrffitting"
        )

install_requires = [
        "numpy>=1.18.1",
        "compwizard>=0.1.2",
	"scipy>=1.4.1"
        ]

if __name__ == "__main__":
    setup(**setup_args, install_requires=install_requires)
