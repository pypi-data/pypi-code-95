from __future__ import print_function
from setuptools import setup, find_packages

setup(
    name="hdpca",
    version="0.1.5",
    author="rileyge",  # 作者名字
    author_email="rlge@live.com",
    description="Hign Dimensional PCA. Including D2PCA and D2SquarePCA in 0.1.X versions.",
    license="Apache 2.0",
    url="https://gitee.com/rlge/hdpca",  # github地址或其他地址
    packages=find_packages(),
    include_package_data=True,
    # classifiers=[
    #     "Environment :: Web Environment",
    #     'Intended Audience :: Developers',
    #     'License :: Apache 2.0',
    #     'Operating System :: MacOS',
    #     'Operating System :: Microsoft',
    #     'Operating System :: Unix',
    #     'Topic :: Meachine Learning',
    #     'Topic :: Libraries :: Python Modules',
    #     'Programming Language :: Python :: 3.8'
    # ],
    install_requires=[
            'numpy>=1.14.0'   # 所需要包的版本号
    ],
    zip_safe=True,
)
