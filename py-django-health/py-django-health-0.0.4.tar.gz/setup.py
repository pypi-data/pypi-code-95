from setuptools import setup


with open('README.md', 'r') as md:
    long_description = md.read()

setup(
  name='py-django-health',
  version='0.0.4',
  author='kencinas95',
  author_email='kencinas95@developers.com',
  description='Health checkers for Django apps',
  long_description=str(long_description),
  long_description_content_type='text/markdown',
  url='https://github.com/kencinas95/py-django-health',
  license='GPLv3',
  packages=['health', 'health.checkers'],
  keywords=['health', 'checkers', 'heartbeat', 'microservices'],
  install_requires=[
    'django',
    'pydantic'
  ],
  python_requires=">=3.6",
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8'
  ]
)
