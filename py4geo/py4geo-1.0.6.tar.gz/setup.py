import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py4geo",
    version="1.0.6",
    author="Manuele Pesenti",
    author_email="manuele@inventati.org",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/manuelep/py4vtile",
    project_urls={
        "Bug Tracker": "https://github.com/manuelep/py4vtile/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    package_data={"": ['*.sql', '*.md']},
    python_requires=">=3.6",
    install_requires=[
        "overpy",
        "shapely",
        "ujson",
        "pyproj",
        "mercantile",
        "lxml",
        "geojson",
        "hashids",
        "tqdm",
        "geomet",
        "h3",
        "mptools>=1.0.7",
        "py4vtile",
        "supermercado",
        "osm2geojson"
    ]
)
