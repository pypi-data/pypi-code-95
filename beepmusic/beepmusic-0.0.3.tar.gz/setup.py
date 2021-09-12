import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="beepmusic",
    version="0.0.3",
    author="Chris Pan",
    author_email="pgx@pku.edu.cn",
    description="Play music using computer beep prompt tone.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChrisChemHater/BeepMusic",
    project_urls={
        "Bug Tracker": "https://github.com/ChrisChemHater/BeepMusic/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    package_data={"beepmusic": ["builtin_musics/*.bmc"]},
    python_requires=">=3.6",
)