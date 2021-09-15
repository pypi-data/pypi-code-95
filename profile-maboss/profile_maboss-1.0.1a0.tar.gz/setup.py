from setuptools import setup, find_packages

setup(name='profile_maboss',
    version="1.0.1a",
    author="Rémi Trimbour",
    author_email="remi.trimbour@ens.fr",
    description="A package allowing personalisation of MaBoSS models with the PROFILE methodology defined in [paper_ref]",
	install_requires = ['maboss'],
	packages=['profile_maboss'],
)