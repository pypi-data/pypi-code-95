import sys
import setuptools

from src.stitch_m import __version__, __author__
from src.stitch_m.file_handler import dragndrop_bat_file

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements=[
    "tifffile>=2020.9.30",
    "mrcfile>=1.1.2",
    "numpy>=1.21.1",
    "omexml-dls>=1.1.0",
    "pywin32;platform_system=='Windows'"
    ]

batch_script_string = f"""{sys.executable} -m stitch_m %*
"""

if dragndrop_bat_file.exists():
    dragndrop_bat_file.unlink()
with open(dragndrop_bat_file, "x") as f:
    f.write(batch_script_string)

setuptools.setup(
    name="StitchM",
    version=__version__,
    author=__author__,
    author_email="thomas.fish@diamond.ac.uk",
    description="A package for stitching mosaics from Cockpit with (or without) ROIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license_files=["LICENSE",],
    url="https://github.com/DiamondLightSource/StitchM",
    install_requires=requirements,
    packages=setuptools.find_packages('src', exclude=('scripts', 'tests')),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    package_data={'stitch_m': ['config.cfg']},
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            "StitchM = stitch_m.scripts.commandline:main",
            "stitchm = stitch_m.scripts.commandline:main"
            ]
            },
    test_suite='src.tests',
    extras_require={
        "scalene": ["scalene"],
    }
)
