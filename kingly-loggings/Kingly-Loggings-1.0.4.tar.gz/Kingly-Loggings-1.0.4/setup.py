from setuptools import find_packages, setup

setup(
    name='Kingly-Loggings',
    version='1.0.4',
    author='CHK141',
    author_email='chk141@139.com',
    # description='自用Logger类,仅支持Python3',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    # packages=['Loggings'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'loguru', 'pathlib'
    ],
)

