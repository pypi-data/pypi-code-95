import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GoogleDriveWrapper",
    version="0.1.7",
    author="João Paulo",
    author_email="jpmarques@ufrn.edu.br",
    description="A small package to make it easier work with GoogleDrive",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jpmarques-97",
    project_urls={
        "Bug Tracker": "https://github.com/jpmarques-97",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[
          'pandas',
          'numpy',
          'google-api-python-client',
          'google-auth-httplib2',
          'google-auth-oauthlib',
          'oauth2client',
          'httplib2'
      ]
)
