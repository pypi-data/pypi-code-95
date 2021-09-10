import setuptools
import discord
requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

extras_require = {
    "http": ["aiohttp", "async-timeout", "typing-extensions", "multidict", "attrs", "yarl", "chardet"]
}
setuptools.setup(
  name='aiohoripy',
  author='lvlahraam',
  url='https://github.com/lvlahraam/aiohoripy',
  version="0.0.2",
  license='MIT',
  description='An asynchronous Python Wrapper for Hori-API',
  long_description=long_description,
  long_description_content_type="text/markdown",
  python_requires='>=3.8.0',
  packages=setuptools.find_packages(),
  include_package_data=True,
  install_requires=[
    "aiohttp",
    "async-timeout",
    "typing-extensions",
    "multidict",
    "attrs",
    "yarl",
    "chardet"
  ],
  keywords=["python", "api", "discord", "http", "anime", "hori"],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Topic :: Internet',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
    'Topic :: Internet :: WWW/HTTP :: Session',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
    'Typing :: Typed',
  ]
)