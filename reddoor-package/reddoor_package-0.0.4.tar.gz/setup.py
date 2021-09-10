from setuptools import _install_setup_requires, setup

longdesc=""
with open("README.md", "r") as f:
    longdesc = f.read()

setup(
    name='reddoor_package',
    version='0.0.4',
    description='Reddoor public package',
    py_modules=['reddoor_gcp'],
    package_dir={'':'src'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    long_description = longdesc,
    long_description_content_type = "text/markdown",
    install_requires=["arrow","pymysql","google-cloud-storage","google-cloud-bigquery"]
)