from setuptools import setup

version = "0.1.2.3"

long_description = "Python module for edu-tpi.donstu"

setup(
	name="tpilib",
	version=version,

	author="Feb",
	author_email="drons_dron@mail.ru",

	description = long_description,
	long_description=long_description,

	url = "https://github.com/febdaynik/tpilib",

	packages=["tpilib"],
	install_reqires=["requests"],
)

