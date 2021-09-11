from setuptools import find_packages, setup


install_requires = (
    "aiohttp>=3.7.4",
    "yarl>=1.3.0",
    "aiojobs>=0.2.2",
    "aiozipkin>=0.7.0",
    "marshmallow>=3.13.0",
)

setup(
    name="neuro-notifications-client",
    python_requires=">=3.8",
    url="https://github.com/neuro-inc/neuro-notifications-client",
    packages=find_packages(),
    install_requires=install_requires,
    zip_safe=False,
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    include_package_data=True,
)
