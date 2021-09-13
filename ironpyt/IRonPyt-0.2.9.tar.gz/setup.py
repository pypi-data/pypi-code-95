import setuptools

with open("README.md", "r") as fh:
    description = fh.read()
from setuptools import setup, find_packages
setuptools.setup(
    name="IRonPyt",
    version="0.2.9",
    author="berre",
    packages=find_packages(),
    package_data={'': ['*.dll'], '': ['src/*.so'], '': ['data/*.cvs']},  # This is the most important line.
    zip_safe=False,
    include_package_data=True,
    author_email="berreergunn@gmail.com",
    description="A sample test package",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/gituser/test-tackage",
    license='MIT',
    python_requires='>=2',
    install_requires=["pywin32 >= 1.0;platform_system=='Windows'","matplotlib",'numpy','pandas','sklearn']
)