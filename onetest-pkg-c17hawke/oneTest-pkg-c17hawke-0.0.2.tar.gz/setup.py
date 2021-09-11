import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

PROJECT_NAME = "oneTest"
USER_NAME = "c17hawke"

setuptools.setup(
    name=f"{PROJECT_NAME}-pkg-{USER_NAME}",
    version="0.0.2",
    author=USER_NAME,
    author_email="sunny.c17hawke@gmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{USER_NAME}/{PROJECT_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{USER_NAME}/{PROJECT_NAME}/issues",
    },
    license="GNU",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "numpy"
    ] # your dependent packages here
)