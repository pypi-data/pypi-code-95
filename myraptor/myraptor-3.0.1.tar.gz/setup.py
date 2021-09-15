from setuptools import setup

def get_long_description():
    with open('README.md') as f:
        long_description = f.read()

REQUIREMENTS = ['requests']

setup(name='myraptor',
      version='3.0.1',
      description='Prague public transport connection finder using RAPTOR algorithm',
      long_description=get_long_description(),
      url='https://github.com/hanjak/connection_finder_prague_mhd',
      author='Hana Kosova',
      author_email='hanja.kosova@gmail.com',
      license='MIT',
      packages=['myraptor'],
      install_requires=['pandas==1.3.2','numpy==1.21.2'],
      keywords='raptor connection finder',
      include_package_data=True,
      package_data={'myraptor':['data/data.csv','data/data_stops.csv']},
      )