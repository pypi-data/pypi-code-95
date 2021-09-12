import setuptools

with open("README.md", "r", encoding="utf-8") as f:
	long_description = f.read()


setuptools.setup(
	name="chk_args",
	version="1.1",
	author="kurages",
	author_email="kurages.dev@gmail.com",
	description="アノテーションチェッカー",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/kurages/python_annotations_checker",
	project_urls={
		"Bug Tracker": "https://github.com/kurages/python_annotations_checker/issues",
	},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	package_dir={"": "src"},
	packages=setuptools.find_packages(where="src"),
	python_requires=">=3.6",
)

