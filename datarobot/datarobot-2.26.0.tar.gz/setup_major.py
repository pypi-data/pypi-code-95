from setuptools import find_packages, setup

from common_setup import common_setup_kwargs, DESCRIPTION_TEMPLATE, version

if "b" in version:
    msg = (
        "Major releases must not have a 'b' for beta in the version. "
        "Go back and make a release branch with tag, then update the version number."
    )
    raise RuntimeError(msg)

description = DESCRIPTION_TEMPLATE.format(
    package_name="datarobot",
    pypi_url_target="https://pypi.python.org/pypi/datarobot/",
    extra_desc="",
    pip_package_name="datarobot",
    docs_link="https://datarobot-public-api-client.readthedocs-hosted.com",
)

packages = find_packages(exclude=["tests*", "*_experimental*"])

common_setup_kwargs.update(
    name="datarobot", version=version, packages=packages, long_description=description,
)

setup(**common_setup_kwargs)
