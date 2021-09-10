import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nclearn",
    version="0.0.1",
    author="Necmettin Ceylan",
    author_email="necmettinceylan@hotmail.com",
    description="A personal scikit-learn like library to practice ml algorithms and software development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NecmettinCeylan/nclearn",
    project_urls={
        "Bug Tracker": "https://github.com/NecmettinCeylan/nclearn/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
