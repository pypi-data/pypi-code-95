from setuptools import setup, find_packages

file = open("README.md", "r");
README = file.read();
file.close();
setup(name = "simpleSound", version = "1.0.1", author = "nekumelon", author_email = "nekumelon@gmail.com", long_description_content_type = "text/markdown", long_description = README, packages = find_packages(), description = "A very very very simple sound playing library for windows.", url = "https://github.com/nekumelon/simpleSound", license = "MIT", install_requires = [""]);