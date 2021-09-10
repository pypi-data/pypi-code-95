import io
from os import path
from setuptools import setup


this_directory = path.abspath(path.dirname(__file__))
long_description = ''
with io.open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="django-s3sign",
    version="0.2.1",
    author="Anders Pearson",
    author_email="ctl-dev@columbia.edu",
    url="https://github.com/ccnmtl/django-s3sign",
    description="Django view for AWS S3 signing",
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['Django>=1.11', 'nose', 'boto3', 'botocore'],
    scripts=[],
    license="GPL3",
    platforms=["any"],
    zip_safe=False,
    package_data={'': ['*.*']},
    packages=['s3sign'],
    test_suite='nose.collector',
    include_package_data=True,
)
