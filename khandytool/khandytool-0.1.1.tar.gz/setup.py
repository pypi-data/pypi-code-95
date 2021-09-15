import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="khandytool",
    version="0.1.1",
    author="Ou Peng",
    author_email="kevin72500@qq.com",
    description="khandytool, handy core in testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kevin72500/khandytool",
    packages=setuptools.find_packages(),
    install_requires=['faker==8.12.1','jmespath==0.9.5','loguru==0.4.1','pymysql==1.0.2'],
    entry_points={
        'console_scripts': [
            'khandytool=khandytool:core'
        ],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)