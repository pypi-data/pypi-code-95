import setuptools #模块
with open("README.md","rb") as f:
    description=f.read().decode("utf-8")

setuptools.setup(
    name="package01",
    version="1.0",
    packages=setuptools.find_packages(),
    author="laozhang",
    author_email="aaa@163.com",
    description="一个打包案例",
    long_description=description,
    python_requires=">=3.7"
)