from setuptools import setup

setup(name='seems-legit-cache',
      version='0.1.0',
      description="A dict-based cache that's probably fine to use",
      long_description=open('README.md').read(),
      author='Luc Perkins',
      author_email='lucperkins@gmail.com',
      license='MIT',
      packages=['seemslegitcache'],
      url='https://github.com/lucperkins/seems-legit-cache',
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'expiringdict'
      ])
