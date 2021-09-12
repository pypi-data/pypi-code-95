from setuptools import setup, find_packages

setup(
    name='page_query',
    version='0.1.5',
    description='collect, index and query pages from everywhere',
    author='amazinglzy',
    author_email='forlearn_lzy@163.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'pyyaml',
        'requests',
        'elasticsearch',
        'rich'
    ],
    entry_points={
        'console_scripts': [
            'pq = page_query.main:main',
        ],
    },
)