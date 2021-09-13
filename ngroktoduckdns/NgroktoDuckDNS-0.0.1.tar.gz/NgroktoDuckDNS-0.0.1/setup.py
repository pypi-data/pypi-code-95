from setuptools import setup

__name__ = 'NgroktoDuckDNS'
__description__ = 'Expose local services to the web through duckdns with ngrok.'
__version__ = '0.0.1'
__author__ = 'GrandMoff100'
__author_email__ = 'nlarsen23.student@gmail.com'


setup(
    name=__name__,
    description=__description__,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    modules=['ngroktoduckdns'],
    install_requires=['click', 'pyngrok', 'requests'],
    entry_points={
        'console_scripts': 'ngroktoduckdns = ngroktoduckdns:cli'
    }
)