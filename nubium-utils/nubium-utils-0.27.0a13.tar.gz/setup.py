import setuptools

with open("README.md", "r") as file_obj:
    long_description = file_obj.read()

install_requires = [
    "prometheus_client",
    "requests",
    "pytz",
    "python-dateutil",
    "nubium-schemas>=1.1.2a"
]

confluent_requires = [
    "confluent-kafka[avro]==1.6.1"
]

faust_requires = [
    "cython==0.29.17",
    "faust[rocksdb]==1.10.4",
    "idna<3",
    "chardet",
    "python-schema-registry-client",
]

dev_requires = confluent_requires + faust_requires + [
    "pytest",
    "twine",
]

packages = setuptools.find_packages()

setuptools.setup(
    name="nubium-utils",
    version="0.27.0a13",
    author="Edward Brennan",
    author_email="ebrennan@redhat.com",
    description="Some Kafka utility functions and patterns for the nubium project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.corp.redhat.com/mkt-ops-de/nubium-utils.git",
    packages=packages,
    install_requires=install_requires,
    extras_require={"dev": dev_requires, "confluent": confluent_requires, "faust": faust_requires},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
