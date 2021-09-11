import os.path
import setuptools

current_dir = os.path.dirname(__file__)

with open(os.path.join(current_dir, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

with open(os.path.join(current_dir, "turbineml/version.py"), "r", encoding="utf-8") as f:
    version_file = f.read()

version = None
for line in version_file.splitlines():
    if line.startswith('__version__'):
        delim = '"' if '"' in line else "'"
        version = line.split(delim)[1]
if version is None:
    raise RuntimeError("Version not found")

with open(os.path.join(current_dir, "requirements.txt"), "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()


setuptools.setup(
    name="turbineml",
    version=version,
    author="Turbine ML",
    author_email="info@turbineml.com",
    description="Turbine ML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/turbineml/turbine-client",
    project_urls={
        "Bug Tracker": "https://github.com/turbineml/turbine-client/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(exclude=[]),
    install_requires=requirements,
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'turbine = turbineml.cli.main:main'
        ],
    },
)