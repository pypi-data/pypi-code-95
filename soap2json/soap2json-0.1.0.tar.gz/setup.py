import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
      name='soap2json',
      version='0.1.0',
      description='Soap to Json',
      author='Wilson Silva',
      author_email='wilson.silva@bcn.cv',
      license='MIT',
      zip_safe=False,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/bcn-dev/soap2json.git",
      package_dir={"": "src"},
      packages=setuptools.find_packages(where="src"),
      python_requires=">=3.9",
      project_urls={
            "Bug Tracker": "https://github.com/bcn-dev/soap2json/issues",
      },
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      install_requires=[
            'appdirs==1.4.4',
            'attrs==21.2.0',
            'cached-property==1.5.2',
            'certifi==2021.5.30',
            'charset-normalizer==2.0.4',
            'defusedxml==0.7.1',
            'idna==3.2',
            'isodate==0.6.0',
            'lxml==4.6.3',
            'pytz==2021.1',
            'requests==2.26.0',
            'requests-file==1.5.1',
            'requests-toolbelt==0.9.1',
            'six==1.16.0',
            'urllib3==1.26.6',
            'xmltodict==0.12.0',
            'zeep==4.0.0',
      ]
 )