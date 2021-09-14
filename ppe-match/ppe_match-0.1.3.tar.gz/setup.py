from setuptools import setup, find_packages
# import pkg_resources
import pathlib

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='ppe_match',
    version='0.1.3',
    description=' Intuitive framework that allows researchers to implement and test matching methodologies',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=find_packages(),
    author='Ram Bala, Michele Samorani, Rohit Jacob',
    author_email='rbala@scu.edu, msamorani@scu.edu, rohitjacob92@gmail.com',
    keywords=['matching','ppe','framework','matcha','frappe'],
    url='https://github.com/samorani/MatchingPPE',
    include_package_data=True,
	package_data={'': ['data/*']},
	install_requires=['pandas','numpy']
)

# with pathlib.Path('requirements.txt').open() as requirements_txt:
#     install_requires = [
#         str(requirement) for requirement in pkg_resources.parse_requirements(requirements_txt)
#     ]

classifiers=[
  'Development Status :: 4 - Beta', # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
  'Intended Audience :: Developers',
  'Topic :: Software Development :: Build Tools',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3',
  'Programming Language :: Python :: 3.4',
  'Programming Language :: Python :: 3.5',
  'Programming Language :: Python :: 3.6',
  'Programming Language :: Python :: 3.7',
  'Programming Language :: Python :: 3.8',
  'Programming Language :: Python :: 3.9'
]

if __name__ == '__main__':
    setup(**setup_args,
			classifiers=classifiers)
