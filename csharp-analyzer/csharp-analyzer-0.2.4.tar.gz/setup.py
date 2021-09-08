import setuptools

with open("README.md", "r") as f:
	long_description = f.read()

with open("requirements.txt", "r") as f:
	requirements = f.read()


setuptools.setup(
	name="csharp-analyzer",
	version="0.2.4",
	author="Daniil Antonov",
	author_email="danil.antonov.05@gmail.com",
	description="This package can help you to smash and present C# code into OOP style",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/luc1f-a/csharp-analyzer",
	packages=setuptools.find_packages(),
	install_requires=requirements,
	classifiers=[
		"Programming Language :: Python :: 3.9",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	# Требуемая версия Python.
	python_requires='>=3.9.5',
)
