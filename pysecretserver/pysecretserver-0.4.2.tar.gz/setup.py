from setuptools import setup

setup(
    name='pysecretserver',
    version='0.4.2',
    description='A Python library for interacting with the SecretServer REST API.',
    url='https://gitlab.com/dcs-tech/devops/pysecretserver',
    author='Christopher Kay',
    author_email='christopher.kay@dcs.tech',
    license='Apache2',
    packages=['pysecretserver'],
    install_requires=[
        'requests',
    ],
    zip_safe=False,
    keywords=['secretserver'],
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3"
    ]
)
