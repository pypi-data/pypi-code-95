from setuptools import setup, find_packages

setup(
    name="SDTapi",
    version="0.2.5",
    author="bmd",
    author_email="1790523836@qq.com",
    description="SDT测试产品",
    python_requires=">=3.8",
    package_dir={'': 'src'},
    packages=find_packages('src'),

    # include_package_data = True
    package_data = {"":["Scripts/*.pyd"]}
)


