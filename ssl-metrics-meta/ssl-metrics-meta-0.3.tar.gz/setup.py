from setuptools import setup

from ssl_metrics_meta import version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ssl-metrics-meta",
    packages=["ssl_metrics_meta"],
    version=version.version(),
    description="SSL Metrics - Helper Project to Install All SSL Metrics Projects",
    author="Software and Systems Laboratory - Loyola University Chicago",
    author_email="ssl-metrics@ssl.luc.edu",
    license="BSD",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://ssl.cs.luc.edu/projects/metricsDashboard",
    project_urls={
        "Bug Tracker": "https://github.com/SoftwareSystemsLaboratory/ssl-metrics/issues",
        "GitHub Repository": "https://github.com/SoftwareSystemsLaboratory/ssl-metrics",
    },
    keywords=[
        "git",
        "github",
        "software engineering",
        "metrics",
        "software systems laboratory",
        "ssl",
        "loyola",
        "loyola university chicago",
        "luc",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.9",
    install_requires=[
        "ssl-metrics-github-issues",
        "ssl-metrics-git-commits-loc",
        "ssl-metrics-json-converter"
    ],
    entry_points={},
)
