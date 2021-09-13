from setuptools import find_packages, setup

from common_setup import common_setup_kwargs, DESCRIPTION_TEMPLATE, version

description = DESCRIPTION_TEMPLATE.format(
    package_name="datarobot",
    pypi_url_target="https://pypi.python.org/pypi/datarobot/",
    extra_desc="",
    pip_package_name="datarobot",
    docs_link="https://datarobot-public-api-client.readthedocs-hosted.com",
)

packages = find_packages(exclude=["tests"])

common_setup_kwargs.update(
    name="datarobot", version=version, packages=packages, long_description=description,
)

setup(**common_setup_kwargs)
