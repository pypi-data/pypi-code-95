import setuptools,os

with open("ReadMe.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open('requirements.txt') as f:
    requirements = f.readlines()
with open("aws_sts_tool{}_version.py".format(os.path.sep),encoding='utf-8') as f:
    version = f.read().strip().split(" = ")[1][1:-1]

setuptools.setup(
    name="aws_sts_tool",
    version=version,
    author="Mohammad Faraz",
    author_email="farazm708@gmail.com",
    description="A CLI tool to help assume AWS role via STS.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/farazmd/aws-sts-tool",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(exclude=['tests']),
    entry_points ={
            'console_scripts': [
                'aws_sts_tool = aws_sts_tool.cli:main'
            ]
        },
    python_requires=">=3.7",
)