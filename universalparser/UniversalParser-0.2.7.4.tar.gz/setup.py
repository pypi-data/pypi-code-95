import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="UniversalParser",
    version="0.2.7.4",
    author="jiyang",
    author_email="jiyangj@foxmail.com",
    description="一款通用的文本格式解析器，支持XML、JSON、YAML、HTML、XHTML、Word、Excel、PPT等文本格式的快速解析，在方法上具有高度一致性。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/jiyangj/universal-parser",
    packages=setuptools.find_packages(),
    install_requires=[],
    python_requires='>=3.5',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)