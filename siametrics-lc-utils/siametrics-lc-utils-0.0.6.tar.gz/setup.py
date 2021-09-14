import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='siametrics-lc-utils',
    version='0.0.6',
    packages=setuptools.find_namespace_packages(include=['siametrics.lc.*']),
    url='',
    license='Apache 2.0',
    author='SSripilaipong',
    author_email='santhapon.s@siametrics.com',
    python_requires='>=3.7',
    description='Siametrics Logistics Core Utils',
    install_requires=requirements,
)
