from setuptools import setup, find_packages

setup(
    name='Kingly_Loggings',
    version='1.0.61',
    author='CHK141',
    author_email='chk141@139.com',
    # description='自用Logger类,   仅支持Python3',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    # packages=['Loggings'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'loguru', 'pathlib'
    ],
)

