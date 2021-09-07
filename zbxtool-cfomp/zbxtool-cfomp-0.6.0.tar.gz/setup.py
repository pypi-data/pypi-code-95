from setuptools import setup, find_packages

with open("requirements.txt") as reqs_file:
    reqs = reqs_file.readlines()

setup(
    name ="zbxtool-cfomp",
    packages = find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires = reqs,
    use_scm_version = {
        "relative_to": __file__,
        "local_scheme": "no-local-version",
    },
    entry_points={
        'console_scripts':[
            'zbxtool = lib.cli:main'
        ],
    },
    setup_requires = ['setuptools_scm']
)
