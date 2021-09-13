from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='base-qualitest-package',
      version='1.0.2',
      description='Qualitest package automation infrastructure kit tools for GUI and API tests',
      url='https://upload.pypi.org/legacy/',
      author='Yossi & Moshe',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='MIT',
      packages=['general', 'rest_api', 'selenium_base', 'shared', 'unit_tests'],
      zip_safe=False,
      use_scm_version=True,
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.5',
      )