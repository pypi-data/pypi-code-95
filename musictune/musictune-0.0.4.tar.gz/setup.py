import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="musictune",
    version="0.0.4",
    author="vibujithan",
    author_email="author@example.com",
    description="Parallel image processing package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vibujithan/musictune",
    project_urls={
        "Bug Tracker": "https://github.com/vibujithan/musictune/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    package_data={
        "musictune": ["data/**", "data/PSF/**"],
        "": ["examples/**"]
    },
    scripts=['src/musictune/scripts/pzf2zarr.py', 'src/musictune/scripts/start_cluster.py',
             'src/musictune/scripts/temp.py'
             ]
)
