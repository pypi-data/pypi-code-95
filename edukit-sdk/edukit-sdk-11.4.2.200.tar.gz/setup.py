#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from setuptools import setup, find_packages

setup(
    name='edukit-sdk',
    author='Huawei',
    version='11.4.2.200',
    url='https://developer.huawei.com/consumer/cn/doc/development/'
        'AppGallery-connect-Guides/edukit-introduction-0000001050822201',
    author_email='opencapability@huawei.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy==1.19.5', 'opencv-contrib-python==4.2.0.34',
        'opencv-python==4.4.0.46'
    ]
)
