import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()
    print(long_description)
    
version={}
with open("obsinfo/version.py") as fp:
    exec(fp.read(),version)

setuptools.setup(
    name="obsinfo",
    version=version['__version__'],
    author="Wayne Crawford",
    author_email="crawford@ipgp.fr",
    description="Tools for documenting ocean bottom seismometer experiments and creating metadata",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://gitlab.com/resif/obsinfo/-/tree/v0.110/obsinfo",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
          'numpy>=1',
          'obspy>=1.1',
          'pyyaml>=3.0',
          'jsonschema>=2.6',
          'python-gitlab>=2.9.0',
          'jsonref>=0.2'
      ],
    entry_points={
        'console_scripts': [
            'obsinfo-validate=obsinfo.main.validate:main',
            'obsinfo-makeStationXML=obsinfo.main.makeStationXML:main',
            'obsinfo-print=obsinfo.main.print:print_obs',
            'obsinfo-setup=obsinfo.main.setupObsinfo:setup_obsinfo',
            'obsinfo-test=obsinfo.tests.test:run_suite_info_files',
            'obsinfo-print_version=obsinfo.print_version:main',
            'obsinfo-make_SDPCHAIN_scripts=obsinfo.addons.SDPCHAIN:_console_script',
            'obsinfo-make_LCHEAPO_scripts=obsinfo.addons.LCHEAPO:_console_script'
        ]
    },
    python_requires='>=3',
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    classifiers=(
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics"
    ),
    keywords='seismology OBS'
)
