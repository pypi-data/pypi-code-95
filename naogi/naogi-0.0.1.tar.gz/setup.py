import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="naogi",
    version="0.0.1",
    author="Evgeny Breykin",
    author_email="zbrejkin@yandex.ru",
    description="Abstract class for Naogi ML deployment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Naogi/naogi_model",
    project_urls={
        "Bug Tracker": "https://github.com/Naogi/naogi_model/issues",
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
