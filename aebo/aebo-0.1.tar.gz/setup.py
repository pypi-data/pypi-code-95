from setuptools import setup

setup(name='aebo',
      version='0.1',
      description='This package is for ABG robot',
      url='http://www.aeroboticsglobal.com/',
      author='Aerobotics Global',
      author_email='lokeshkode@aeroboticsglobal.com',
      license='MIT',
      packages=['aebo'],
      install_requires=[
          'nltk',
          'scikit-learn',
      ],
      zip_safe=False)
