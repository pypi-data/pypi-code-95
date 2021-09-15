import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wdltest",
    version="1.15.0",
    author="Marcin Piechota",
    author_email="piechota.marcin@gmail.com",
    description="Package for testing wdl workflows",
    #long_description=long_description,
    #long_description_content_type="text/reStructuredText",
    url="https://github.com/marpiech/wdltest",
    packages=setuptools.find_packages(),
    package_data={'wdltest': ['*.cfg']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['threaded','regex'],
    python_requires='>=3.6',
    scripts=['bin/wdltest'],
    test_suite='nose.collector',
    tests_require=['nose>=1.0'],
    setup_requires=['nose>=1.0'],
)
