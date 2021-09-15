from setuptools import setup, find_packages

# https://github.com/QuantConnect/Lean/blob/master/LICENSE
with open('./LICENSE') as f:
    license = f.read()

with open('README.md') as f:
    readme = f.read()

setup(
     name='algotech',
     version='0.1',
     description = 'AlgoTech API',
     long_description=readme,
     author = 'Julian Wiley',
     author_email = 'julian@julianwiley.com',
     url='https://algotechcapital.com',
     license=license,
     packages = find_packages(exclude=('tests', 'docs')),
     install_requires=['matplotlib', 'pandas', 'requests']
     )