from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

# noinspection PyPackageRequirements
setup(
    name="battlenet_client",
    version="1.2.0rc3",
    author="David \"Gahd\" Couples",
    author_email="gahdania@gahd.io",
    description="Battle.net REST API Connections",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/battlenet1/bnet",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests_oauthlib', 'python-decouple'],
    python_requires='>=3.8',
)
