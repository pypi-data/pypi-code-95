from setuptools import setup

setup(
    name='python-amazon-ad-api',
    version='0.0.2',
    install_requires=[
        "requests",
        "six",
        "cachetools~=4.2.2",
        "pycryptodome",
        "python-dotenv",
        "pytz",
        "confuse",
    ],
    packages=['ad_api','ad_api.api','ad_api.auth','ad_api.base','ad_api.api.sp'],
    url='https://github.com/denisneuf/ad_api',
    license='MIT',
    author='Daniel',
    author_email='info@leadtech.es',
    description='Python wrapper for the Amazon Advertising API'
)