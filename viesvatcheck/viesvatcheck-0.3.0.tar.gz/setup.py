from setuptools import setup, find_packages

setup(
    name='viesvatcheck',
    version='0.3.0',
    url='https://github.com/shulcsm/vies-vat-check',
    author='Mārtiņš Šulcs',
    author_email='shulcsm@gmail.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    license='MIT',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    install_requires=[
       'zeep>=4.0.0',
    ]
)
