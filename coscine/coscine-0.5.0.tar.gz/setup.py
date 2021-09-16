import setuptools
from src.coscine.about import __version__, __author__

with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setuptools.setup(
	name = "coscine",
	version = __version__,
	description = "Coscine Python Client",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	author = __author__,
	author_email = "coscine@itc.rwth-aachen.de",
	license = "MIT License",
	packages = setuptools.find_packages(where="src"),
	keywords = [
		"Coscine", "RWTH Aachen", "Research Data Management"
	],
	install_requires = [
		"requests",
		"requests-toolbelt",
		"tqdm",
		"colorama",
		"boto3"
	],
	url = "https://git.rwth-aachen.de/coscine/docs/public/coscine-python-client",
	project_urls = {
		"Issues":  "https://git.rwth-aachen.de/coscine/docs/public/coscine-python-client/-/issues",
		"Wiki": "https://git.rwth-aachen.de/coscine/docs/public/coscine-python-client/-/wikis/home"
	},
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Intended Audience :: Developers"
	],
	package_dir = {"": "src"},
	python_requires = ">=3.7"
)