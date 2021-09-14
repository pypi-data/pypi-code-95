

'''
        'pandas >= 2.0', # 버전 특정
        'requests',      # 최신버전 설치
        "pywin32 >= 1.0;platform_system=='Windows'", # 플랫폼 구분
        'importlib; python_version = "3.8"',
        #packages=['coxem'],
'''

from setuptools import setup, find_packages
setup(
    name='coxem',
    version='0.0.0.3',
    author='programmerJ',
    author_email='jade74.work@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
    ],
)