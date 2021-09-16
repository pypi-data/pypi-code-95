from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="syneto-clio",
    version="0.2.3",
    author="Alexandra Veres",
    author_email="alexandra.veres@syneto.eu",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Click"],
    entry_points="""
        [console_scripts]
        syneto-clio = syneto_clio:cli
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
