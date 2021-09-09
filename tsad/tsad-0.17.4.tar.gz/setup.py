from setuptools import setup, find_packages
 
setup(name='tsad',
      version='0.17.4',
      url='https://github.com/waico/tsad',
      license='BSD-3-Clause License',
      #packages=find_packages(),
      packages=['tsad'],
      author='Vyacheslav Kozitsin, Iurii Katser',
      author_email='rfptk2525@yandex.ru',
      description='Time Series Deep Learning Anomaly Detection',
      #packages=find_packages(exclude=['tests']),
      long_description=open('./tsad/README.md').read(),
      #long_description_content_type='text/x-rst',
      install_requires=['numpy>=1.19.5','pandas>=1.0.1','matplotlib>=3.1.3','scikit-learn>=0.24.1','torch==1.5.0'], # install_requires=[ 'A>=1,<2', 'B>=2']
      zip_safe=False)