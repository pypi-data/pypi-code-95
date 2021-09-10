from setuptools import setup, find_packages

setup(
    name='brforest',
    version='1.0.0',
    description='Scikit compatible implementation of random forests with bayesian vote aggregation introduced in '
                '"Decision-forest voting scheme for classification of rare classes in network intrusion detection" '
                'by Brabec and Machlica at IEEE SMC 2018',
    url="https://github.com/JanBrabec/brforest",
    author='Jan Brabec',
    author_email='brabecjan91@gmail.com',
    packages=find_packages(exclude=['notebooks', 'test']),
    include_package_data=True,
    install_requires=['numpy>=1.20.3,<2', 'scikit-learn>=0.24.2'],
    tests_require=['pytest>=6.2.5,<7']
)
