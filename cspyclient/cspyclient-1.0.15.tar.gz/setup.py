from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='cspyclient',
  version='1.0.15', # production
  # version='1.0.8', # staging
  description='An internal tool to work with CoderSchool Backend API',
  author='Minh Hai Do',
  author_email='minhdh@coderschool.vn',
  license='MIT', 
  classifiers=classifiers,
  packages=['cspyclient'],
  install_requires=['pandas', 'requests', 'cryptography', 'numpy'],
  tests_require=['pytest']
)