from setuptools import setup
from setuptools import find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()


def get_version():
    with open("pyranch/__init__.py") as f:
        for line in f:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1])


with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name = 'pyranch',
    version = get_version(),
    packages = find_packages(),
    author = 'Federico Torresan',
    author_email = 'federico.torresan@quentral.com',
    url = 'https://github.com/fedetorre/pyranch',
    license = 'LGPLv3',
    install_requires=required,
    description="Rancher API SDK",
    long_description = readme,
    long_description_content_type="text/markdown",
    classifiers = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
