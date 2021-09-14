from setuptools import setup, find_packages

setup(
    name="mkdocs-opensource",
    version='0.0.1',
    url='',
    license='',
    description='oceanbase static site theme',
    author='zhouzi',
    author_email='3222676446@qq.com',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'mkdocs.themes': [
            'open_source_theme = open_source_theme',
        ]
    },
    zip_safe=False
)
