from setuptools import setup





def readme():
    with open('README.rst') as file:
        return file.read()


setup(name='resqlconnection',
      version='1.0',
      description='The RE crawling tool',
      author="Andreas Rystad, Alex Hodgson",
      author_email="TechnologySupport@rystadenergy.com",
      license="MIT",  # ?
      packages=["RESqlConnection"],
      install_requires=[
          'pandas>1.3.0', 'numpy>1.21.0', 'SQLAlchemy>1.4.20', 'pyodbc>4.0.30', 'pymssql>2.2.1', 'setuptools>56.0.0'
      ],
      zip_safe=False)
