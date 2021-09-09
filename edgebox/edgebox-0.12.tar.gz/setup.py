from setuptools import setup
import edgebox

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='edgebox',
      version=edgebox.__version__,
      description='Edgebox for MobiledgeX',
      long_description=readme(),
      url='http://github.com/mobiledgex/edgebox',
      author='Venky Tumkur',
      author_email='venky.tumkur@mobiledgex.com',
      license='MIT',
      packages=['edgebox'],
      entry_points={
          'console_scripts': ['edgebox=edgebox.command_line:main'],
      },
      python_requires='>=3.6, <4',
      install_requires=[
          'PyYAML>=5.3.1',
          'requests>=2.23.0',
          'Tempita>=0.5.2',
      ],
      include_package_data=True,
      zip_safe=False)
