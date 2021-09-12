import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("./requirements.txt", "r") as rh:
    requirements = rh.read().splitlines()


setuptools.setup(
    name="jat-queue",
    version="0.0.1",
    author="Vinay G B",
    author_email="vinaygb665@gmail.com",
    description="Just another task queue",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VinayGb665/jat-queue",
    project_urls={
        "Bug Tracker": "https://github.com/VinayGb665/jat-queue/issues",
    },
    package_data={'': ['*']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    entry_points ={
        'console_scripts': [
            'jatq = executors.main:package_cli'
        ]
    },
    install_requires=requirements,
    package_dir={"": "./"},
    packages=setuptools.find_packages(where="./"),
    python_requires=">=3.9",
    
)