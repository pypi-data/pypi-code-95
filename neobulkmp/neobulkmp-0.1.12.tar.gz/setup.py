from setuptools import setup

setup(
    name="neobulkmp",
    description="Tool for multiprocessed dataloading into a neo4j db, without node blocking",
    url="",
    author="Tim Bleimehl",
    author_email="tim.bleimehl@helmholtz-muenchen.de",
    license="MIT",
    packages=["neobulkmp"],
    install_requires=[
        "py2neo",
        "graphio",
        "linetimer",
        "redis",
        "jsonpickle",
        "psutil",
        "humanfriendly",
    ],
    extras_require={"test": ["DZDutils"]},
    python_requires=">=3.6",
    zip_safe=False,
    include_package_data=True,
    use_scm_version={
        "root": ".",
        "relative_to": __file__,
        # "local_scheme": "node-and-timestamp"
        "local_scheme": "no-local-version",
        "write_to": "version.py",
    },
    setup_requires=["setuptools_scm"],
)
