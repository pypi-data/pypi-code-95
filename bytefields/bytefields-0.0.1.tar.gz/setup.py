from setuptools import setup, find_packages

setup(name='bytefields',
      version='0.0.1',
      description='Python byte field manipulation',
      author='Zach Morris',
      author_email='zacharymorr@outlook.com',
      package_dir={"": "src"},
      packages=find_packages(where='src')
)