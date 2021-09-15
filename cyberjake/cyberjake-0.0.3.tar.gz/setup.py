from setuptools import setup
from cyberjake import __version__

install_reqs = open("requirements.txt").readlines()
test_reqs = open("requirements-dev.txt").readlines()

readme = open("README.md").read()

setup(
        name="cyberjake",
        version=__version__,
        description="Common code used in my programs",
        long_description=readme,
        long_description_content_type="text/markdown",
        author="Cyber_Jake",
        author_email="jake@jwhite.network",
        url="https://github.com/Cyb3r-Jak3/common-python",
        project_urls={
            "Changelog": "https://github.com/Cyb3r-Jak3/common-python/blob/main/CHANGELOG.md",
            "Issues": "https://github.com/Cyb3r-Jak3/common-python/issues"
        },
        download_url="https://github.com/Cyb3r-Jak3/common/releases/latest",
        packages=[
            "cyberjake"
        ],
        package_dir={"cyberjake": "cyberjake"},
        tests_require=test_reqs[1:],
        install_requires=install_reqs,
        license="MPL 2.0",
        zip_safe=False,
        keywords="common, cyb3rjak3",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
            "Natural Language :: English",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: Implementation :: CPython"
        ],
)
