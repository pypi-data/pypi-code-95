from setuptools import find_packages, setup
setup(
    name='geodesicDome',
    packages=find_packages(include=['geodesicDome']),
    version='0.1.0',
    install_requires=["numpy", "numba"],
    description='My first Python library',
    author='Me',
    license='MIT',
)