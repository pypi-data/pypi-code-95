from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Developers',
  'Topic :: Software Development :: Build Tools',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3',
  'Programming Language :: Python :: 3.4',
  'Programming Language :: Python :: 3.5',
  'Programming Language :: Python :: 3.6'
]
 
setup(
  name='samp_data_generation',
  version='1.0.8',
  description='This python library handles synthetic data generation for the Omdena-SAMP project.',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Samuel Nnitiwe Theophilus',
  author_email='nnitiwe@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='object detection, synthetic data', 
  packages=find_packages(),
  install_requires=['numpy','pillow','opencv-python','scikit-image'] 
)

